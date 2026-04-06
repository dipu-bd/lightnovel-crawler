from typing import Any, Iterable, List, Optional, TypeVar

import sqlmodel as sq
from sqlalchemy.orm import aliased
from sqlmodel import Session

from ...context import ctx
from ...dao import Job, JobPriority, JobStatus, JobType, OutputFormat, User, UserRole
from ...exceptions import ServerErrors
from ...server.models import Paginated
from ...server.tier import JOB_PRIORITY_LEVEL
from ...utils.time_utils import current_timestamp
from .utils import select_ancestors, select_descendends

T = TypeVar("T")

job_status_type = Job.__table__.c.status.type  # type: ignore
job_failed_literal = sq.cast(sq.literal(JobStatus.FAILED.name), job_status_type)
job_success_literal = sq.cast(sq.literal(JobStatus.SUCCESS.name), job_status_type)
job_running_literal = sq.cast(sq.literal(JobStatus.RUNNING.name), job_status_type)
job_canceled_literal = sq.cast(sq.literal(JobStatus.CANCELED.name), job_status_type)


class JobService:
    def __init__(self) -> None:
        pass

    # -------------------------------------------------------------------------
    #                               GET Jobs
    # -------------------------------------------------------------------------
    def list(
        self,
        offset: int = 0,
        limit: int = 20,
        *,
        user_id: Optional[str] = None,
        job_type: Optional[JobType] = None,
        priority: Optional[JobPriority] = None,
        status: Optional[JobStatus] = None,
        is_done: Optional[bool] = None,
        parent_job_id: Optional[str] = None,
    ) -> Paginated[Job]:
        with ctx.db.session() as sess:
            stmt = sq.select(Job)
            cnt = sq.select(sq.func.count()).select_from(Job)

            # Apply filters
            conditions: List[Any] = []
            if user_id is not None:
                conditions.append(Job.user_id == user_id)
            if parent_job_id is not None:
                conditions.append(Job.parent_job_id == parent_job_id)
            else:
                conditions.append(sq.col(Job.parent_job_id).is_(None))
            if job_type is not None:
                conditions.append(Job.type == job_type)
            if status is not None:
                conditions.append(Job.status == status)
            if is_done is not None:
                conditions.append(sq.col(Job.is_done).is_(True))
            if priority is not None:
                conditions.append(Job.priority == priority)

            if conditions:
                stmt = stmt.where(*conditions)
                cnt = cnt.where(*conditions)

            # Apply sorting
            if parent_job_id is not None:
                stmt = stmt.order_by(sq.asc(Job.created_at))
            else:
                stmt = stmt.order_by(sq.desc(Job.created_at))

            # Apply pagination
            stmt = stmt.offset(offset).limit(limit)

            total = sess.exec(cnt).one()
            items = sess.exec(stmt).all()

            return Paginated(
                total=total,
                offset=offset,
                limit=limit,
                items=list(items),
            )

    def get(self, job_id: str) -> Job:
        with ctx.db.session() as sess:
            job = sess.get(Job, job_id)
            if not job:
                raise ServerErrors.no_such_job
            return job

    def get_user_id(self, job_id: str) -> Optional[str]:
        with ctx.db.session() as sess:
            stmt = sq.select(Job.user_id).where(Job.id == job_id)
            return sess.exec(stmt).first()

    def verify_access(self, user: User, job_id: str) -> str:
        user_id = self.get_user_id(job_id)
        if not user_id:
            raise ServerErrors.no_such_job
        if user_id != user.id and user.role != UserRole.ADMIN:
            raise ServerErrors.forbidden
        return user_id

    def get_children_ids(self, parent_job_id: str) -> Iterable[str]:
        with ctx.db.session() as sess:
            stmt = sq.select(Job.id).where(Job.parent_job_id == parent_job_id)
            return sess.exec(stmt).all()

    def get_children(self, parent_job_id: str) -> Iterable[Job]:
        with ctx.db.session() as sess:
            stmt = sq.select(Job).where(Job.parent_job_id == parent_job_id)
            return sess.exec(stmt).all()

    def get_chapter_job(self, user: User, chapter_id: str) -> Optional[Job]:
        with ctx.db.session() as sess:
            return sess.exec(
                sq.select(Job)
                .where(
                    Job.user_id == user.id,
                    Job.type == JobType.CHAPTER,
                    sq.col(Job.parent_job_id).is_(None),
                    Job.extra["chapter_id"].as_string() == chapter_id,
                )
                .limit(1)
            ).first()

    def get_root(self, job_id: str) -> Optional[Job]:
        with ctx.db.session() as sess:
            sa_pars = select_ancestors(job_id)
            return sess.exec(
                sq.select(Job)
                .where(sq.col(Job.id).in_(sa_pars))
                .where(sq.col(Job.parent_job_id).is_(None))
                .limit(1)
            ).first()

    # -------------------------------------------------------------------------
    #                              CREATE Jobs
    # -------------------------------------------------------------------------
    def fetch_novel(
        self,
        user: User,
        url: str,
        *,
        full: bool = False,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        ctx.sources.get_crawler(url)  # validate
        data.update({"url": url})
        novel = ctx.novels.find_by_url(url)
        if novel:
            data["novel_id"] = novel.id
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.FULL_NOVEL if full else JobType.NOVEL,
        )

    def fetch_many_novels(
        self,
        user: User,
        *urls: str,
        full: bool = False,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update({"urls": urls})
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.FULL_NOVEL_BATCH if full else JobType.NOVEL_BATCH,
        )

    def fetch_volume(
        self,
        user: User,
        volume_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        volume = ctx.volumes.get(volume_id)
        data.update(
            {
                "volume_id": volume_id,
                "volume_serial": volume.serial,
            }
        )
        if not data.get("novel_title"):
            novel = ctx.novels.get(volume.novel_id)
            data.update(
                {
                    "novel_id": novel.id,
                    "novel_title": novel.title,
                }
            )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.VOLUME,
        )

    def fetch_many_volumes(
        self,
        user: User,
        *volume_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update(
            {
                "volume_ids": volume_ids,
            }
        )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.VOLUME_BATCH,
        )

    def fetch_chapter(
        self,
        user: User,
        chapter_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        chapter = ctx.chapters.get(chapter_id)
        data.update(
            {
                "chapter_id": chapter_id,
                "chapter_serial": chapter.serial,
            }
        )
        if not data.get("novel_title"):
            novel = ctx.novels.get(chapter.novel_id)
            data.update(
                {
                    "novel_id": novel.id,
                    "novel_title": novel.title,
                }
            )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.CHAPTER,
        )

    def fetch_many_chapters(
        self,
        user: User,
        *chapter_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update(
            {
                "chapter_ids": chapter_ids,
            }
        )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.CHAPTER_BATCH,
        )

    def fetch_image(
        self,
        user: User,
        image_id: str,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        image = ctx.images.get(image_id)
        data.update(
            {
                "image_id": image_id,
                "url": image.url,
            }
        )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.IMAGE,
        )

    def fetch_many_images(
        self,
        user: User,
        *image_ids: str,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update(
            {
                "image_ids": image_ids,
            }
        )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.IMAGE_BATCH,
        )

    def make_artifact(
        self,
        user: User,
        novel_id: str,
        format: OutputFormat,
        *,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update(
            {
                "novel_id": novel_id,
                "format": format,
            }
        )
        if not data.get("novel_title"):
            novel = ctx.novels.get(novel_id)
            data.update(
                {
                    "novel_title": novel.title,
                }
            )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.ARTIFACT,
        )

    def make_many_artifacts(
        self,
        user: User,
        novel_id: str,
        *formats: OutputFormat,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
        **data: Any,
    ) -> Job:
        data.update(
            {
                "novel_id": novel_id,
                "formats": formats,
            }
        )
        if not data.get("novel_title"):
            novel = ctx.novels.get(novel_id)
            data.update(
                {
                    "novel_title": novel.title,
                }
            )
        return self._create(
            user=user,
            data=data,
            parent_id=parent_id,
            depends_on=depends_on,
            type=JobType.ARTIFACT_BATCH,
        )

    # -------------------------------------------------------------------------
    #                              DELETE Jobs
    # -------------------------------------------------------------------------
    def delete(self, job_id: str) -> None:
        with ctx.db.session() as sess:
            result = sess.exec(
                sq.select(Job.done, Job.total, Job.failed).where(Job.id == job_id)
            ).first()
            if not result:
                return
            done, total, failed = result

            self._update_up(
                sess,
                job_id=job_id,
                done=Job.done - done,
                total=Job.total - total,
                failed=Job.failed - failed,
            )

            sa_deps = select_descendends(job_id, True)
            sess.exec(sq.delete(Job).where(sq.col(Job.id).in_(sa_deps)))

            sess.commit()

    # -------------------------------------------------------------------------
    #                              CANCEL Jobs
    # -------------------------------------------------------------------------

    def cancel(self, job_id: str, who: str = "admin") -> None:
        with ctx.db.session() as sess:
            self._cancel_down(sess, job_id, True)
            self._fail(
                sess,
                job_id,
                reason=f"Canceled as the parent job was canceled by {who}",
            )
            self._update(
                sess,
                job_id,
                error=f"Canceled by {who}",
                status=job_canceled_literal,
            )
            sess.commit()

    # -------------------------------------------------------------------------
    #                            Internal Methods
    # -------------------------------------------------------------------------
    def _create(
        self,
        user: User,
        type: JobType,
        data: dict,
        parent_id: Optional[str] = None,
        depends_on: Optional[str] = None,
    ) -> Job:
        with ctx.db.session() as sess:
            job = Job(
                type=type,
                extra=data,
                user_id=user.id,
                depends_on=depends_on,
                parent_job_id=parent_id,
                priority=JOB_PRIORITY_LEVEL[user.tier],
            )
            sess.add(job)

            self._update_up(
                sess,
                job.id,
                total=Job.total + 1,
            )

            sess.commit()
            sess.refresh(job)
            return job

    def _pending(
        self,
        artifact: Optional[bool] = None,
        skip_job_ids: Iterable[str] = [],
        skip_user_ids: Iterable[str] = [],
    ) -> Optional[Job]:
        with ctx.db.session() as sess:
            stmt = sq.select(Job)

            job_alias = aliased(Job)
            dep_is_done = (
                sq.exists(1)
                .where(sq.col(job_alias.id) == Job.depends_on)
                .where(sq.col(job_alias.is_done).is_(True))
            )
            stmt = stmt.where(sq.or_(sq.col(Job.depends_on).is_(None), dep_is_done))

            job_is_new = sq.and_(
                Job.status == JobStatus.RUNNING,
                Job.done == 0,
            )
            stmt = stmt.where(
                sq.or_(
                    Job.status == JobStatus.PENDING,
                    job_is_new,
                )
            )

            if skip_job_ids:
                stmt = stmt.where(sq.col(Job.id).not_in(skip_job_ids))

            if skip_user_ids:
                stmt = stmt.where(
                    sq.or_(
                        Job.priority != JobPriority.LOW, sq.col(Job.user_id).not_in(skip_user_ids)
                    )
                )

            if artifact is not None:
                if artifact:
                    stmt = stmt.where(Job.type == JobType.ARTIFACT)
                else:
                    stmt = stmt.where(Job.type != JobType.ARTIFACT)

            stmt = stmt.order_by(
                sq.desc(Job.priority),
                sq.asc(Job.updated_at),
            )
            return sess.exec(stmt.limit(1)).first()

    def _update(self, sess: Session, job_id: str, **values) -> None:
        sess.exec(sq.update(Job).where(sq.col(Job.id) == job_id).values(**values))

    def _update_up(
        self,
        sess: Session,
        job_id: str,
        done=Job.done,
        total=Job.total,
        failed=Job.failed,
        inclusive: bool = False,
    ) -> None:
        now = current_timestamp()

        sa_done = done
        sa_total = total
        sa_failed = failed
        sa_is_done = sa_done == sa_total

        sa_status = sq.case((sa_is_done, job_success_literal), else_=Job.status)
        sa_started_at = sq.case(
            (sq.and_(sa_is_done, sq.col(Job.started_at).is_(None)), now), else_=Job.started_at
        )
        sa_finished_at = sq.case(
            (sq.and_(sa_is_done, sq.col(Job.finished_at).is_(None)), now), else_=Job.finished_at
        )

        sa_pars = select_ancestors(job_id, inclusive)
        sess.exec(
            sq.update(Job)
            .where(sq.col(Job.id).in_(sa_pars))
            .where(sq.col(Job.is_done).is_(False))
            .values(
                done=sa_done,
                total=sa_total,
                failed=sa_failed,
                status=sa_status,
                is_done=sa_is_done,
                started_at=sa_started_at,
                finished_at=sa_finished_at,
            )
        )

    def _cancel_down(self, sess: Session, job_id: str, inclusive=False) -> None:
        now = current_timestamp()
        sa_deps = select_descendends(job_id, inclusive)
        sess.exec(
            sq.update(Job)
            .where(
                sq.col(Job.id).in_(sa_deps),
                sq.col(Job.is_done).is_(False),
            )
            .values(
                is_done=True,
                status=job_canceled_literal,
                error="Canceled by one of the parent",
                started_at=sq.func.coalesce(Job.started_at, now),
                finished_at=sq.func.coalesce(Job.finished_at, now),
            )
        )

    def _increment_up(self, sess: Session, job_id: str, step: int = 1) -> None:
        self._update_up(
            sess,
            job_id=job_id,
            inclusive=True,
            done=Job.done + step,
        )

    def _count_pending(self, sess: Session, job_id: str) -> int:
        return sess.exec(sq.select(Job.total - Job.done).where(Job.id == job_id)).one()

    def _success(self, sess: Session, job_id: str) -> None:
        pending = self._count_pending(sess, job_id)
        self._increment_up(sess, job_id, pending)

    def _fail(self, sess: Session, job_id: str, reason: str) -> None:
        pending = self._count_pending(sess, job_id)
        self._update_up(
            sess,
            job_id=job_id,
            inclusive=True,
            done=Job.done + pending,
            failed=Job.failed + pending,
        )
        self._update(
            sess,
            job_id,
            error=reason,
            status=job_failed_literal,
        )

    def cancel_if_dangling(self, job: Job) -> bool:
        root = self.get_root(job.id)
        if root and not root.is_done:
            return False

        self.cancel(job.id)
        if root:
            if root.status == JobStatus.CANCELED:
                self.cancel(root.id)
            else:
                with ctx.db.session() as sess:
                    self._cancel_down(sess, root.id, False)
                    sess.commit()

        return True
