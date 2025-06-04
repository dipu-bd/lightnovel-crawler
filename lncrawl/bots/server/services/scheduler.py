import logging
from threading import Event, Thread
from typing import Dict, Optional

from sqlmodel import asc, desc, or_, select

from ..context import ServerContext
from ..models.job import Job, JobStatus
from .runner import microtask

logger = logging.getLogger(__name__)

CONCURRENCY = 5


class JobScheduler:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx
        self.db = ctx.db
        self.signal: Optional[Event] = None

    def close(self):
        self.stop()

    @property
    def running(self):
        return self.signal and not self.signal.is_set()

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
        if self.signal:
            self.signal.set()
            self.signal = None

    def run(self, signal=Event()):
        logger.info('Scheduler started')
        try:
            while not signal.is_set():
                signal.wait(self.ctx.config.app.runner_cooldown)
                if signal.is_set():
                    break
                logger.debug('Running scheduled task')
                try:
                    self.__task(signal)
                except KeyboardInterrupt:
                    raise
                except Exception:
                    logger.exception('Failed to complete scheduled run')

                logger.debug('Finished scheduled task')
        except KeyboardInterrupt:
            signal.set()
        finally:
            logger.info('Scheduler stoppped')

    def __task(self, signal=Event()):
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

            threads: Dict[Optional[str], Thread] = {}
            for job in jobs:
                if job.novel_id in threads:
                    continue  # no concurrency for same novel
                t = Thread(
                    target=microtask,
                    args=(sess, job, signal),
                    daemon=True,
                )
                t.start()
                threads[job.novel_id] = t

            for t in threads.values():
                if t.is_alive():
                    t.join(1)
