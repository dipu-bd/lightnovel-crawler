import logging
import traceback
from functools import cached_property
from threading import Event
from typing import Any, Dict, Iterable, Optional, Set

from ...context import ctx
from ...dao import Artifact, Job, JobStatus, JobType, NotificationItem, OutputFormat
from ...exceptions import AbortedException
from ...utils.event_lock import EventLock
from ...utils.time_utils import current_timestamp

logger = logging.getLogger(__name__)

_lock = EventLock()
_queue: Dict[str, Event] = {}
_users: Dict[str, str] = {}


class JobRunner:
    @staticmethod
    def run(signal: Event, artifact: bool):
        try:
            with _lock.using(signal):
                job = ctx.jobs._pending(
                    artifact,
                    skip_job_ids=_queue.keys(),
                    skip_user_ids=_users.values(),
                )
                if not job:
                    job = ctx.jobs._pending(
                        artifact,
                        skip_user_ids=_users.values(),
                    )
                    return
                if not job:
                    return
                if job.parent_job_id:
                    if ctx.jobs.cancel_if_dangling(job):
                        logger.debug(f"Dangling job [b]{job.id}[/b] | {job.job_title}")
                        return
                _queue[job.id] = Event()
                _users[job.id] = job.user_id

            try:
                JobRunner(job, _queue[job.id]).process()
            finally:
                with _lock.using(signal):
                    if job.id in _queue:
                        _queue.pop(job.id).set()
                        _users.pop(job.id)
        except Exception:
            logger.error("Unexpected error in runner", exc_info=True)

    @staticmethod
    def cancel(job_id: str):
        if job_id in _queue:
            _queue.pop(job_id).set()
            _users.pop(job_id)
        for job_id in ctx.jobs.get_children_ids(job_id):
            JobRunner.cancel(job_id)

    @staticmethod
    def cancel_all():
        for signal in _queue.values():
            signal.set()
        _queue.clear()
        _users.clear()

    def __init__(self, job: Job, signal=Event()) -> None:
        self.job = job
        self.signal = signal
        self.children: Iterable[Job] = []

    @cached_property
    def user(self):
        return ctx.users.get(self.job.user_id)

    def process(self) -> bool:
        message = f"[cyan]{self.job.status.name}[/cyan] [b]{self.job.id}[/b] | {self.job.job_title}"
        if not self.job.parent_job_id:
            logger.info(message)
        else:
            logger.debug(f"{message}")

        if self.job.is_running:
            self.children = ctx.jobs.get_children(self.job.id)
            if all(job.is_done for job in self.children):
                return self.__set_done()

        if self.job.type == JobType.FULL_NOVEL_BATCH:
            return self._novel_batch()
        if self.job.type == JobType.NOVEL_BATCH:
            return self._novel_batch()
        if self.job.type == JobType.FULL_NOVEL:
            return self._novel()
        if self.job.type == JobType.NOVEL:
            return self._novel()
        if self.job.type == JobType.VOLUME_BATCH:
            return self._volume_batch()
        if self.job.type == JobType.VOLUME:
            return self._volume()
        if self.job.type == JobType.CHAPTER_BATCH:
            return self._chapter_batch()
        if self.job.type == JobType.CHAPTER:
            return self._chapter()
        if self.job.type == JobType.IMAGE_BATCH:
            return self._image_batch()
        if self.job.type == JobType.IMAGE:
            return self._image()
        if self.job.type == JobType.ARTIFACT_BATCH:
            return self._artifact_batch()
        if self.job.type == JobType.ARTIFACT:
            return self._artifact()

        return self.__set_done(f"Job type is not supported: [b]{self.job.type}[/b]")

    # ------------------------------------------------------------------ #
    #                               Helpers                              #
    # ------------------------------------------------------------------ #

    def __refresh(self):
        with ctx.db.session() as sess:
            self.job = sess.get_one(Job, self.job.id)

    def __set_running(self) -> None:
        with ctx.db.session() as sess:
            now = current_timestamp()
            ctx.jobs._update(
                sess,
                self.job.id,
                started_at=now,
                status=JobStatus.RUNNING,
            )
            sess.commit()
            self.job.started_at = now
            self.job.status = JobStatus.RUNNING
        self.__send_mail()

    def __increment(self) -> bool:
        with ctx.db.session() as sess:
            ctx.jobs._increment_up(sess, self.job.id)
            sess.commit()
        self.__refresh()
        self.__send_mail()
        return True

    def __set_done(self, error: str = "", err_source: Optional[Exception] = None) -> bool:
        if error and err_source:
            lines = traceback.format_exception(
                type(err_source),
                value=err_source,
                tb=err_source.__traceback__,
                chain=True,
            )
            lines += ["", error]
            error = "".join(lines)
        with ctx.db.session() as sess:
            if error:
                ctx.jobs._fail(sess, self.job.id, error.strip())
            else:
                ctx.jobs._success(sess, self.job.id)
            sess.commit()
        self.__refresh()
        self.__send_mail()
        return not error

    def __set_extra(self, **values: Any) -> None:
        extra = dict(**self.job.extra)
        for k, v in values.items():
            extra[k] = v
        with ctx.db.session() as sess:
            ctx.jobs._update(
                sess,
                self.job.id,
                extra=extra,
            )
            sess.commit()
            self.job.extra = extra

    def __send_mail(self):
        if not self.user.is_verified:
            return

        if self.job.parent_job_id:
            parent = ctx.jobs.get_root(self.job.id)
            if not parent:
                return
            runner = JobRunner(parent, self.signal)
            runner.user = self.user
            return runner.__send_mail()

        alert_items: Set[NotificationItem] = set()
        all_notifications = set(NotificationItem)
        email_alerts = self.user.extra.get("email_alerts") or {}
        email_sent = set(self.job.extra.get("email_sent") or [])
        for k, v in email_alerts.items():
            if not v or v in email_sent:
                continue
            if int(k) not in all_notifications:
                continue
            alert_items.add(NotificationItem(int(k)))

        if not alert_items:
            return

        if NotificationItem.JOB_SUCCESS in alert_items:
            if self.job.status == JobStatus.SUCCESS:
                ctx.mail.send_job_report(self.user, self.job)
                email_sent.add(NotificationItem.JOB_SUCCESS.value)

        if NotificationItem.JOB_RUNNING in alert_items:
            if self.job.status == JobStatus.RUNNING:
                ctx.mail.send_job_report(self.user, self.job)
                email_sent.add(NotificationItem.JOB_RUNNING.value)

        if NotificationItem.JOB_CANCELED in alert_items:
            if self.job.status == JobStatus.CANCELED:
                ctx.mail.send_job_report(self.user, self.job)
                email_sent.add(NotificationItem.JOB_CANCELED.value)

        if NotificationItem.JOB_FAILURE in alert_items:
            if self.job.status == JobStatus.FAILED:
                ctx.mail.send_job_report(self.user, self.job)
                email_sent.add(NotificationItem.JOB_FAILURE.value)

        if NotificationItem.NOVEL_SUCCESS in alert_items:
            if self.job.status == JobStatus.SUCCESS and (
                self.job.type == JobType.FULL_NOVEL or self.job.type == JobType.NOVEL
            ):
                ctx.mail.send_full_novel_job_success(self.user, self.job)
                email_sent.add(NotificationItem.NOVEL_SUCCESS.value)
        if NotificationItem.ARTIFACT_SUCCESS in alert_items:
            if self.job.status == JobStatus.SUCCESS and (
                self.job.type == JobType.ARTIFACT or self.job.type == JobType.ARTIFACT_BATCH
            ):
                ctx.mail.send_full_novel_job_success(self.user, self.job)
                email_sent.add(NotificationItem.ARTIFACT_SUCCESS.value)

        self.__set_extra(email_sent=list(email_sent))

    # ------------------------------------------------------------------ #
    #                             Job Runners                            #
    # ------------------------------------------------------------------ #

    def _novel_batch(self) -> bool:
        try:
            urls = self.job.extra.get("urls")
            if not urls:
                return self.__set_done()

            urls = set(urls)
            if self.job.is_running:
                urls -= set([job.extra.get("url") for job in self.children])
            else:
                self.__set_running()

            full = self.job.type == JobType.FULL_NOVEL_BATCH
            for url in sorted(urls):
                if self.signal.is_set():
                    raise AbortedException()
                ctx.jobs.fetch_novel(self.user, url, full=full, parent_id=self.job.id)

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _novel(self) -> bool:
        try:
            url = self.job.extra.get("url")
            if not url:
                return self.__set_done("No novel url")

            added_types = {}
            if self.job.is_running:
                added_types = {job.type: job.id for job in self.children}
            else:
                self.__set_running()

            novel = ctx.crawler.fetch_novel(
                self.user.id,
                url,
                self.signal,
            )
            self.__set_extra(novel_id=novel.id)

            if self.job.type != JobType.FULL_NOVEL:
                return self.__set_done()

            if JobType.VOLUME_BATCH not in added_types:
                volumes = ctx.volumes.list(novel_id=novel.id)
                if not volumes:
                    return self.__set_done()

                job = ctx.jobs.fetch_many_volumes(
                    self.user,
                    *(volume.id for volume in volumes),
                    parent_id=self.job.id,
                    novel_id=novel.id,
                    novel_title=novel.title,
                )
                added_types[job.type] = job.id

            if JobType.ARTIFACT not in added_types:
                ctx.jobs.make_artifact(
                    self.user,
                    novel.id,
                    OutputFormat.epub,
                    parent_id=self.job.id,
                    novel_title=novel.title,
                    depends_on=added_types[JobType.VOLUME_BATCH],
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to fetch novel", e)

    def _volume_batch(self) -> bool:
        try:
            volume_ids = self.job.extra.get("volume_ids")
            if not volume_ids:
                return self.__set_done()

            volume_ids = set(volume_ids)
            if self.job.is_running:
                volume_ids -= set([job.extra.get("volume_id") for job in self.children])
            else:
                self.__set_running()

            for volume_id in volume_ids:
                if self.signal.is_set():
                    raise AbortedException()
                ctx.jobs.fetch_volume(
                    self.user,
                    volume_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get("novel_title"),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _volume(self) -> bool:
        try:
            volume_id = self.job.extra.get("volume_id")
            if not volume_id:
                return self.__set_done("No volume id")

            chapter_ids = set([chapter.id for chapter in ctx.chapters.list(volume_id=volume_id)])

            if self.job.is_running:
                chapter_ids -= set([job.extra.get("chapter_id") for job in self.children])
            else:
                self.__set_running()

            for chapter_id in chapter_ids:
                if self.signal.is_set():
                    raise AbortedException()
                ctx.jobs.fetch_chapter(
                    self.user,
                    chapter_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get("novel_title"),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _chapter_batch(self) -> bool:
        try:
            chapter_ids = self.job.extra.get("chapter_ids")
            if not chapter_ids:
                return self.__set_done()

            chapter_ids = set(chapter_ids)
            if self.job.is_running:
                chapter_ids -= set([job.extra.get("chapter_id") for job in self.children])
            else:
                self.__set_running()

            for chapter_id in chapter_ids:
                if self.signal.is_set():
                    raise AbortedException()
                ctx.jobs.fetch_chapter(
                    self.user,
                    chapter_id,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get("novel_title"),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _chapter(self) -> bool:
        try:
            chapter_id = self.job.extra.get("chapter_id")
            if not chapter_id:
                return self.__set_done("No chapter id")

            added_types = {}
            if self.job.is_running:
                added_types = {job.type: job.id for job in self.children}
            else:
                self.__set_running()

            chapter = ctx.crawler.fetch_chapter(
                self.user.id,
                chapter_id,
                self.signal,
                refresh=(not self.job.parent_job_id),
            )
            if not chapter.is_available:
                return self.__set_done("Failed to fetch contents")

            if JobType.IMAGE_BATCH not in added_types:
                images = ctx.images.list(chapter_id=chapter.id, is_crawled=False)
                if not images:
                    return self.__set_done()

                ctx.jobs.fetch_many_images(
                    self.user,
                    *(image.id for image in images),
                    parent_id=self.job.id,
                    chapter_id=chapter.id,
                    chapter_title=chapter.title,
                    novel_id=chapter.novel_id,
                    novel_title=self.job.extra.get("novel_title"),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to fetch chapter", e)

    def _image_batch(self) -> bool:
        try:
            image_ids = self.job.extra.get("image_ids")
            if not image_ids:
                return self.__set_done()

            image_ids = set(image_ids)
            if self.job.is_running:
                image_ids -= set([job.extra.get("image_id") for job in self.children])
            else:
                self.__set_running()

            for image_id in image_ids:
                if self.signal.is_set():
                    raise AbortedException()
                ctx.jobs.fetch_image(
                    self.user,
                    image_id,
                    parent_id=self.job.id,
                    novel_id=self.job.extra.get("novel_id"),
                    novel_title=self.job.extra.get("novel_title"),
                    chapter_id=self.job.extra.get("chapter_id"),
                    chapter_title=self.job.extra.get("chapter_title"),
                )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _image(self) -> bool:
        try:
            image_id = self.job.extra.get("image_id")
            if not image_id:
                return self.__set_done("No image id")

            if not self.job.is_running:
                self.__set_running()

            image = ctx.crawler.fetch_image(
                self.user.id,
                image_id,
                self.signal,
                refresh=(not self.job.parent_job_id),
            )
            if not image.is_available:
                return self.__set_done("Failed to download image")

            return self.__set_done()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to fetch image", e)

    def _artifact_batch(self) -> bool:
        try:
            novel_id = self.job.extra.get("novel_id")
            if not novel_id:
                return self.__set_done("No novel id")

            formats = self.job.extra.get("formats")
            if not formats:
                return self.__set_done()

            format_job_map = {}
            if self.job.is_running:
                format_job_map = {
                    OutputFormat(job.extra["format"]): job.id for job in self.children
                }
            else:
                self.__set_running()

            added_format = set(format_job_map.keys())
            formats = set(map(OutputFormat, formats))
            need_epub = formats & ctx.binder.depends_on_epub
            if need_epub:
                formats.add(OutputFormat.epub)

            if not formats:
                return self.__set_done()

            for format in sorted(formats - need_epub - added_format):
                if self.signal.is_set():
                    raise AbortedException()
                job = ctx.jobs.make_artifact(
                    self.user,
                    novel_id,
                    format,
                    parent_id=self.job.id,
                    novel_title=self.job.extra.get("novel_title"),
                )
                format_job_map[format] = job.id

            if need_epub:
                epub_job_id = format_job_map.get(OutputFormat.epub)
                if not epub_job_id:
                    return self.__set_done("Failed to create epub request")

                for format in sorted(need_epub - added_format):
                    if self.signal.is_set():
                        raise AbortedException()
                    job = ctx.jobs.make_artifact(
                        self.user,
                        novel_id,
                        format,
                        parent_id=self.job.id,
                        depends_on=epub_job_id,
                    )

            return self.__increment()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to create requests", e)

    def _artifact(self) -> bool:
        try:
            novel_id = self.job.extra.get("novel_id")
            if not novel_id:
                return self.__set_done("No novel id")

            format = self.job.extra.get("format")
            if not format:
                return self.__set_done("No output format")

            if format not in set(OutputFormat):
                return self.__set_done(f"Invalid format: {format}")

            if not self.job.is_running:
                self.__set_running()

            novel_title = self.job.extra.get("novel_title")
            if not novel_title:
                novel_title = ctx.novels.get(novel_id).title

            epub: Optional[Artifact] = None
            if format in ctx.binder.depends_on_epub:
                if not self.job.depends_on:
                    return self.__set_done(f"Dependency job not found for {format}")
                epub = ctx.artifacts.get_epub(self.job.depends_on)

            if self.signal.is_set():
                raise AbortedException()
            artifact = ctx.binder.make_artifact(
                format=format,
                novel_id=novel_id,
                novel_title=novel_title,
                job_id=self.job.id,
                user_id=self.user.id,
                epub=epub,
                signal=self.signal,
            )
            if not artifact.is_available:
                return self.__set_done("Failed to make artifact")

            self.__set_extra(artifact_id=artifact.id, novel_title=novel_title)
            return self.__set_done()
        except AbortedException:
            return False  # ignore error
        except Exception as e:
            return self.__set_done("Failed to make artifact", e)
