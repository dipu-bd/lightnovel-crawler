import logging
from threading import Event, Thread

from sqlmodel import asc, desc, or_, select

from ..context import ServerContext
from ..models.job import Job, JobStatus
from .runner import microtask

logger = logging.getLogger(__name__)


class JobScheduler:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx
        self.db = ctx.db
        self.signal = Event()

    def close(self):
        self.signal.set()

    def start(self):
        Thread(target=self.run, daemon=True).start()

    def run(self):
        logger.info('Scheduler started')
        try:
            while not self.signal.is_set():
                self.signal.wait(self.ctx.config.app.runner_cooldown)
                if self.signal.is_set():
                    break
                logger.debug('Running scheduled task')
                self.__task()
                logger.debug('Finished scheduled task')
        finally:
            logger.info('Scheduler stoppped')

    def __task(self):
        try:
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
                    .limit(5)
                ).all()

                commit = False
                visited = set()
                for job in jobs:
                    if job.novel_id in visited:
                        continue
                    visited.add(job.novel_id)
                    result = microtask(sess, job)
                    if result:
                        commit = True
                if commit:
                    sess.commit()
        except KeyboardInterrupt:
            raise
        except Exception:
            logger.exception('Failed to complete scheduled run')
