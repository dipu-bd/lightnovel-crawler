import logging
from collections import deque
from threading import Event, Thread
from typing import Deque, Dict, Optional

from sqlmodel import asc, desc, or_, select

from ..context import ServerContext
from ..models.job import Job, JobRunnerHistoryItem, JobStatus, RunState
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
                if len(self.threads) < CONCURRENCY:
                    self.__add(signal)
        except KeyboardInterrupt:
            signal.set()
        finally:
            logger.info('Scheduler stoppped')

    def __free(self):
        logger.debug('Waiting for queue to be free')
        # wait for any job to finish
        for k, t in self.threads.items():
            t.join(1)  # wait 1s for this job
            if not t.is_alive():  # if done
                # remove from queue and exit loop
                del self.threads[k]
                break

    def __add(self, signal=Event()):
        logger.debug('Running new task')
        with self.db.session() as sess:
            # fetch jobs based on priority
            stmt = select(Job)
            stmt = stmt.where(
                or_(
                    Job.status == JobStatus.PENDING,
                    Job.status == JobStatus.RUNNING,
                )
            )
            stmt = stmt.order_by(
                desc(Job.priority),
                asc(Job.created_at),
            )
            jobs = sess.exec(stmt).all()

            for job in jobs:
                # cancel duplicate jobs
                if not job.novel_id:
                    job.status = JobStatus.COMPLETED
                    job.run_state = RunState.FAILED
                    job.error = 'Attached novel is not found'
                    sess.add(job)
                    sess.commit()
                    continue

                if job.novel_id in self.threads:
                    if job.status != JobStatus.RUNNING:
                        job.status = JobStatus.COMPLETED
                        job.run_state = RunState.CANCELED
                        job.error = 'Canceled as a duplicate job'
                        sess.add(job)
                        sess.commit()
                    continue

                # if queue is full, wait for the next round,
                # but continue processing pending jobs to detect duplicates
                if len(self.threads) >= CONCURRENCY:
                    continue

                # create and start threads
                t = Thread(
                    target=microtask,
                    args=(job.id, signal),
                    # daemon=True,
                )
                t.start()
                self.threads[job.novel_id] = t

                # log this to history
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
