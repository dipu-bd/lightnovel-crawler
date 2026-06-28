import gc
import logging
from threading import Event, Lock, Thread, current_thread
import time
from typing import Callable, List

from ...context import ctx
from ...exceptions import AbortedException
from .runner import JobRunner
from .scrubber import Scrubber

logger = logging.getLogger(__name__)

# how long stop() waits for all worker threads to exit, in seconds
_STOP_TIMEOUT = 30


def run_scrubber(signal: Event) -> None:
    Scrubber.run(signal)


def run_jobs(signal: Event):
    JobRunner.run(signal, False)


def run_artifact_maker(signal: Event):
    JobRunner.run(signal, True)


def reset_runner(signal: Event):
    JobRunner.reset_stale(ctx.config.crawler.runner_reset_interval)


class JobScheduler:
    def __init__(self) -> None:
        self._threads: List[Thread] = []
        self._state_lock = Lock()
        self._signal = Event()
        self._signal.set()

    def close(self):
        self.stop()

    @property
    def running(self) -> bool:
        return not self._signal.is_set()

    def start(self):
        with self._state_lock:
            if self.running:
                return
            self._signal = Event()
            for i in range(ctx.config.crawler.runner_concurrency):
                self._thread(run_jobs, ctx.config.crawler.runner_cooldown, f"JobRunner-{i}")
            self._thread(run_scrubber, ctx.config.crawler.scrubber_cooldown, "Scrubber")
            self._thread(run_artifact_maker, ctx.config.crawler.runner_cooldown, "ArtifactMaker")
            self._thread(reset_runner, ctx.config.crawler.runner_reset_interval, "RunnerReset")
            logger.info("Scheduler started")

    def stop(self):
        with self._state_lock:
            if not self.running:
                return
            self._signal.set()
            JobRunner.cancel_all()
            deadline = time.monotonic() + _STOP_TIMEOUT
            for t in self._threads:
                t.join(timeout=max(0, deadline - time.monotonic()))
                if t.is_alive():
                    logger.warning(f"Worker {t.name!r} did not stop within {_STOP_TIMEOUT}s")
            self._threads.clear()
            logger.info("Scheduler stopped")
            n_report = gc.collect()
            logger.info(f"GC report: {n_report}")

    def stop_job(self, job_id: str):
        JobRunner.cancel(job_id)

    def _thread(self, run: Callable[[Event], None], interval: int, name: str) -> None:
        t = Thread(
            target=self._loop,
            args=[run, interval],
            name=name,
            daemon=True,  # does not block exit
        )
        t.start()
        self._threads.append(t)

    def _loop(self, run: Callable[[Event], None], interval: int) -> None:
        while self.running:
            try:
                run(self._signal)
                self._signal.wait(interval)
            except AbortedException:
                break
            except Exception:
                logger.error("Unexpected error in scheduler", exc_info=True)
        if self.running:
            logger.warning(f"Worker {current_thread().name!r} exited while scheduler is running")
