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
        self.history: Deque[JobRunnerHistoryItem] = deque(maxlen=20)

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
                self.__add(signal)
        except KeyboardInterrupt:
            signal.set()
        finally:
            logger.info('Scheduler stoppped')

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
                .limit(CONCURRENCY)
            ).all()

            # create threads
            threads: Dict[str, Thread] = {}
            for job in jobs:
                if job.novel_id in threads:
                    continue  # no concurrency for same novel

                t = threads[job.novel_id] = Thread(
                    target=microtask,
                    args=(sess, job, signal),
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

            # wait in same session for completion
            for t in threads.values():
                t.join()
