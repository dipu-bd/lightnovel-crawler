from typing import List, Optional

from pydantic import HttpUrl
from sqlmodel import asc, desc, func, select

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.job import (Artifact, Job, JobDetail, JobPriority, JobStatus,
                          Novel, RunState)
from ..models.pagination import Paginated
from ..models.user import User, UserRole
from .tier import JOB_PRIORITY_LEVEL


class JobService:
    def __init__(self, ctx: ServerContext) -> None:
        self._ctx = ctx
        self._db = ctx.db

    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc",
        user_id: Optional[str] = None,
        novel_id: Optional[str] = None,
        priority: Optional[JobPriority] = None,
        status: Optional[JobStatus] = None,
    ) -> Paginated[Job]:
        with self._db.session() as sess:
            stmt = select(Job)

            # Apply filters
            if user_id:
                stmt = stmt.where(Job.user_id == user_id)
            if novel_id:
                stmt = stmt.where(Job.novel_id == novel_id)
            if status:
                stmt = stmt.where(Job.status == status)
            if priority:
                stmt = stmt.where(Job.priority == priority)

            # Apply sorting
            sort_column = getattr(Job, sort_by, None)
            if sort_column is None:
                raise AppErrors.sort_column_is_none

            if order == "desc":
                stmt = stmt.order_by(desc(sort_column))
            else:
                stmt = stmt.order_by(asc(sort_column))

            total = sess.exec(select(func.count()).select_from(Job)).one()
            jobs = sess.exec(stmt.offset(offset).limit(limit)).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(jobs),
            )

    async def create(self, url: HttpUrl, user: User):
        with self._db.session() as sess:
            # get or create novel
            novel_url = url.encoded_string()
            novel = sess.exec(select(Novel).where(Novel.url == novel_url)).first()
            if not novel:
                novel = Novel(url=novel_url)
                sess.add(novel)

            # create the job
            job = Job(
                user_id=user.id,
                novel_id=novel.id,
                url=novel.url,
                priority=JOB_PRIORITY_LEVEL[user.tier],
            )
            sess.add(job)

            # commit and return
            sess.commit()
            sess.refresh(job)
            return job

    def delete(self, job_id: str, user: User) -> bool:
        with self._db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                return True
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise AppErrors.forbidden
            sess.delete(job)
            sess.commit()
            return True

    def cancel(self, job_id: str, user: User) -> bool:
        with self._db.session() as sess:
            job = sess.get(Job, job_id)
            if not job or job.status == JobStatus.COMPLETED:
                return True
            if job.user_id != user.id and user.role != UserRole.ADMIN:
                raise AppErrors.forbidden
            who = 'user' if job.user_id == user.id else 'admin'
            job.error = f'Canceled by {who}'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.CANCELED
            sess.add(job)
            sess.commit()
            return True

    def get(self, job_id: str) -> JobDetail:
        with self._db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise AppErrors.no_such_job
            return JobDetail(
                job=job,
                user=job.user,
                novel=job.novel,
                artifacts=job.novel.artifacts if job.novel else None,
            )

    def get_artifacts(self, job_id: str) -> List[Artifact]:
        with self._db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise AppErrors.no_such_job
            q = select(Artifact).where(Artifact.novel_id == job.novel_id)
            return list(sess.exec(q).all())

    def get_novel(self, job_id: str) -> Novel:
        with self._db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise AppErrors.no_such_job
            if not job.novel:
                raise AppErrors.no_such_novel
            return job.novel
