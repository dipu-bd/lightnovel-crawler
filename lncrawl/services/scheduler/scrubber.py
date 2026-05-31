import logging
import shutil
from threading import Event

import sqlmodel as sq

from ...context import ctx
from ...dao import Artifact, Job, JobStatus, User, UserToken
from ...exceptions import AbortedException
from ...utils.file_tools import folder_size, format_size
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)
_hour = 3600 * 1000
_day = 24 * _hour
_week = 7 * _day
_month = 30 * _day


class Scrubber:
    def __init__(self, signal=Event()) -> None:
        self.signal = signal

    @staticmethod
    def run(signal: Event):
        scrubber = Scrubber(signal)
        scrubber.free_disk_space()
        scrubber.delete_old_jobs()
        scrubber.cancel_long_jobs()
        scrubber.delete_expired_tokens()
        scrubber.delete_inactive_users()

    def free_disk_space(self):
        # Check if disk size limit is set
        size_limit = ctx.config.crawler.disk_size_limit
        if size_limit <= 0:
            return

        # Check current folder size
        current_size = folder_size(ctx.config.app.app_dir)
        logger.info(f"Current folder size: {format_size(current_size)}")
        if current_size < size_limit:
            return

        # Delete old artifacts
        logger.info("Deleting big artifacts to free up space")
        self.delete_artifacts(current_size, size_limit)

        # Check current folder size
        current_size = folder_size(ctx.config.app.app_dir)
        logger.info(f"Current folder size: {format_size(current_size)}")
        if current_size < size_limit:
            return

        # Delete novel data directories
        logger.info("Deleting novel data to free up space")
        self.delete_novel_data(current_size, size_limit)

        # Check current folder size
        current_size = folder_size(ctx.config.app.app_dir)
        logger.info(f"Current folder size: {format_size(current_size)}")

    def delete_artifacts(self, current_size: int, size_limit: int) -> None:
        now = current_timestamp()

        to_delete = []
        with ctx.db.session() as sess:
            for artifact in sess.exec(
                sq.select(Artifact)
                .where(sq.col(Artifact.created_at) < now - _week)
                .order_by(sq.col(Artifact.file_size).desc())
            ):
                if current_size < size_limit:
                    break
                if self.signal.is_set():
                    raise AbortedException()

                to_delete.append(artifact.id)
                file_path = ctx.files.resolve(artifact.output_file)
                try:
                    current_size -= file_path.stat().st_size
                    file_path.unlink()
                except OSError:
                    logger.debug(f"Error removing: {artifact.id}", exc_info=True)

        # delete all unavailable artifacts
        if len(to_delete) > 0:
            with ctx.db.session() as sess:
                sess.exec(sq.delete(Artifact).where(sq.col(Artifact.id).in_(to_delete)))
                sess.commit()

    def delete_novel_data(self, current_size: int, size_limit: int) -> None:
        to_delete = []

        novel_dirs = list(ctx.files.resolve("novels").iterdir())
        for folder in sorted(novel_dirs, key=lambda p: p.stat().st_mtime):
            if current_size < size_limit:
                break
            if self.signal.is_set():
                raise AbortedException()
            if not folder.is_dir():
                continue

            to_delete.append(folder.name)
            try:
                # empty directory leaving only the cover image
                for file in folder.iterdir():
                    if file.is_dir():
                        current_size -= folder_size(file)
                        shutil.rmtree(file, ignore_errors=True)
                    elif file.name != "cover.jpg":
                        current_size -= file.stat().st_size
                        file.unlink(missing_ok=True)
            except OSError:
                logger.debug(f"Error removing: {folder.name}", exc_info=True)

        # delete all unavailable novel objects
        if len(to_delete) > 0:
            with ctx.db.session() as sess:
                sess.exec(sq.delete(Artifact).where(sq.col(Artifact.novel_id).in_(to_delete)))
                sess.commit()

    def delete_old_jobs(self):
        now = current_timestamp()
        with ctx.db.session() as sess:
            # find root jobs to delete
            job_ids = sess.exec(
                sq.select(Job.id).where(
                    sq.col(Job.parent_job_id).is_(None),
                    Job.status != JobStatus.PENDING,
                    Job.updated_at < now - _month * 3,
                )
            ).all()

            # delete child jobs
            sess.exec(
                sq.delete(Job).where(
                    sq.col(Job.parent_job_id).is_not(None),
                    sq.col(Job.updated_at) < now - _day * 15,
                )
            )
            sess.commit()

        if len(job_ids) > 0:
            logger.info(f"Deleting {len(job_ids)} jobs")
            for job_id in job_ids:
                if self.signal.is_set():
                    return
                ctx.jobs.delete(job_id)

    def cancel_long_jobs(self):
        now = current_timestamp()
        with ctx.db.session() as sess:
            job_ids = sess.exec(
                sq.select(Job.id).where(
                    sq.col(Job.parent_job_id).is_(None),
                    Job.status == JobStatus.RUNNING,
                    Job.updated_at < now - _hour * 16,
                )
            ).all()

        if len(job_ids) > 0:
            logger.info(f"Canceling {len(job_ids)} jobs")
            for job_id in job_ids:
                if self.signal.is_set():
                    return
                ctx.jobs.cancel(job_id)

    def delete_expired_tokens(self):
        now = current_timestamp()
        with ctx.db.session() as sess:
            sess.exec(sq.delete(UserToken).where(sq.col(UserToken.expires_at) < now))
            sess.commit()

    def delete_inactive_users(self):
        now = current_timestamp()
        with ctx.db.session() as sess:
            sess.exec(
                sq.delete(User).where(
                    sq.col(User.is_active).is_not(True),
                    sq.col(User.updated_at) < now - _month,
                )
            )
