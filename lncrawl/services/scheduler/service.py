import gc
import logging
from threading import Event, Thread
from typing import Callable, List, Set

from ...context import ctx
from ...exceptions import AbortedException
from ...utils.event_lock import EventLock
from .runner import JobRunner
from .scrubber import Scrubber

logger = logging.getLogger(__name__)


def run_scrubber(signal: Event) -> None:
    Scrubber.run(signal)


def run_jobs(signal: Event):
    JobRunner.run(signal, False)


def run_artifact_maker(signal: Event):
    JobRunner.run(signal, True)


def reset_runner(signal: Event):
    JobRunner.cancel_all()
    logger.info("Runner reset")


class JobScheduler:
    def __init__(self) -> None:
        self._threads: List[Thread] = []
        self._queue: Set[str] = set()
        self._lock = EventLock()
        self._signal = Event()
        self._signal.set()

    def close(self):
        self.stop()

    @property
    def running(self) -> bool:
        return not self._signal.is_set()

    def start(self):
        if self.running:
            return
        self._signal = Event()
        for _ in range(ctx.config.crawler.runner_concurrency):
            self._thread(run_jobs, ctx.config.crawler.runner_cooldown)
        self._thread(run_scrubber, ctx.config.crawler.scrubber_cooldown)
        self._thread(run_artifact_maker, ctx.config.crawler.runner_cooldown)
        self._thread(reset_runner, ctx.config.crawler.runner_reset_interval)
        logger.info("Scheduler started")

    def stop(self):
        if not self.running:
            return
        self._signal.set()
        JobRunner.cancel_all()
        for t in self._threads:
            t.join()
        self._threads.clear()
        logger.info("Scheduler stoppped")
        n_report = gc.collect()
        logger.info(f"GC report: {n_report}")

    def stop_job(self, job_id: str):
        JobRunner.cancel(job_id)

    def _thread(self, run: Callable[[Event], None], interval: int) -> None:
        t = Thread(
            target=self._loop,
            args=[run, interval],
            daemon=True,  # does not block exit
        )
        t.start()
        self._threads.append(t)

    def _loop(self, run: Callable[[Event], None], interval: int) -> None:
        while self.running:
            try:
                run(self._signal)
                self._signal.wait(interval)
                if self._signal.is_set():
                    return
            except KeyboardInterrupt:
                self._signal.set()
            except AbortedException:
                return
            except Exception:
                logger.error("Unexpected error in scheduler", exc_info=True)
