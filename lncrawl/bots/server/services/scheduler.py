import logging
from collections import deque
from threading import Event, Thread
from typing import Deque, Dict, Optional

from sqlmodel import asc, desc, or_, select

from ..context import ServerContext
from ..models.job import Job, JobRunnerHistoryItem, JobStatus
from ..utils.time_utils import current_timestamp
from .runner import microtask

logger = logging.getLogger(__name__)

CONCURRENCY = 2


class JobScheduler:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx
        self.db = ctx.db
        self.last_run_ts = 0
        self.signal: Optional[Event] = None
        self.threads: Dict[str, Thread] = {}
        self.history: Deque[JobRunnerHistoryItem] = deque(maxlen=50)

    def close(self):
        self.stop()

    @property
    def running(self) -> bool:
        if not self.signal:
            return False
        return not self.signal.is_set()

    def start(self):
        if self.running:
            return
        self.signal = Event()
        Thread(
            target=self.run,
            args=(self.signal,),
            daemon=True,
        ).start()

    def stop(self):
        if not self.signal:
            return
        self.signal.set()
        self.signal = None

    def run(self, signal=Event()):
        logger.info('Scheduler started')
        try:
            while not signal.is_set():
                signal.wait(self.ctx.config.app.runner_cooldown)
                if signal.is_set():
                    return
                self.__free()
                self.__add(signal)
        except KeyboardInterrupt:
            signal.set()
        finally:
            self.__clean()
            logger.info('Scheduler stoppped')

    def __clean(self):
        for k, t in self.threads.items():
            t.join()
        self.threads.clear()

    def __free(self):
        logger.debug('Waiting for queue to be free')
        while len(self.threads) >= CONCURRENCY:
            for k, t in self.threads.items():
                if not t.is_alive():
                    del self.threads[k]
                    break
                t.join(1)

    def __add(self, signal=Event()):
        logger.debug('Running new task')
        with self.db.session() as sess:
            jobs = sess.exec(
                select(Job)
                .where(
                    or_(
                        Job.status == JobStatus.PENDING,
                        Job.status == JobStatus.RUNNING
                    )
                )
                .order_by(
                    desc(Job.priority),
                    asc(Job.created_at),
                )
            ).all()

        # create threads
        for job in jobs:
            if job.novel_id in self.threads:
                continue  # no concurrency for same novel
            if len(self.threads) >= CONCURRENCY:
                return

            t = self.threads[job.novel_id] = Thread(
                target=microtask,
                args=(job.id, signal),
                # daemon=True,
            )
            t.start()

            self.history.append(
                JobRunnerHistoryItem(
                    time=current_timestamp(),
                    job_id=job.id,
                    user_id=job.user_id,
                    novel_id=job.novel_id,
                    status=job.status,
                    run_state=job.run_state,
                )
            )
