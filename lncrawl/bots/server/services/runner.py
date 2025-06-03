import uuid
import logging
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from sqlmodel import asc, desc, select, or_

from lncrawl.core.app import App
from lncrawl.utils.resume_download import (load_all_metadata_from_path,
                                           update_session_from_metadata)

from ..context import ServerContext
from ..exceptions import AppErrors
from ..models.job import (Artifact, Job, JobStatus, Novel, OutputFormat,
                          RunState)
from ..utils.time_utils import current_timestamp


logger = logging.getLogger(__name__)


class JobRunner:
    def __init__(self, ctx: ServerContext) -> None:
        self.ctx = ctx
        self.db = ctx.db
        self.job: Optional[Job] = None

        self.app = App()
        self.token = uuid.uuid4()
        setattr(self.app, 'token', self.token)

    def close(self):
        logger.info('Shutting down')
        self.job = None
        self.app.destroy()
        self._scheduler.shutdown()

    def start(self):
        logger.info('Starting scheduler')
        logging.getLogger("apscheduler").setLevel(logging.WARNING)
        self._scheduler = BackgroundScheduler()
        interval = self.ctx.config.app.runner_interval
        self._scheduler.add_job(
            func=self.run,
            trigger="interval",
            seconds=interval,
            max_instances=1,
            coalesce=False,
        )
        self._scheduler.start()

    def run(self):
        if self.job:
            logger.info(f'Already running a job <{self.job.id}>')
            return

        self.job = self.__get_job()
        if not self.job:
            logger.info('No job to run')
            return

        try:
            if self.job.status == JobStatus.PENDING:
                logger.info(f'[{self.job.id}] Started')
                self.job.status = JobStatus.RUNNING
                self.job.run_state = RunState.PREPARING
                self.job.started_at = current_timestamp()
                self.job.progress = 0
                return

            if self.job.run_state == RunState.PREPARING:
                logger.info(f'[{self.job.id}] Preparing crawling')
                self.__prepare_crawler()
                self.job.run_state = RunState.FETCHING_NOVEL
                self.job.progress = 5
                return

            if self.job.run_state == RunState.FETCHING_NOVEL:
                logger.info(f'[{self.job.id}] Fetching novels')
                self.__fetch_novel()
                self.job.run_state = RunState.FETCHING_CONTENT
                self.job.progress = 10
                return

            self.__prepare_app()

            if self.job.run_state == RunState.FETCHING_CONTENT:
                logger.info(f'[{self.job.id}] Fetching content')
                self.__fetch_content()
                self.job.run_state = RunState.BINDING_NOVEL
                self.job.progress = 80  # 10 to 80
                return

            if self.job.run_state == RunState.BINDING_NOVEL:
                logger.info(f'[{self.job.id}] Binding novel')
                self.__bind_novel()
                self.job.run_state = RunState.UPLOADING_NOVEL
                self.job.progress = 90
                return

            if self.job.run_state == RunState.UPLOADING_NOVEL:
                logger.info(f'[{self.job.id}] Creating artifacts')
                for format in OutputFormat:
                    file = self.app.generated_archives.get(format)
                    if file:
                        self.__create_artifact(format, file)
                self.job.run_state = RunState.SUCCESS
                self.job.progress = 100
                return

            if self.job.run_state == RunState.SUCCESS:
                self.job.status = JobStatus.COMPLETED
                self.job.finished_at = current_timestamp()
                return

        except Exception as e:
            logger.exception(f'[{self.job.id}] Failed')
            self.job.error = repr(e)
            self.job.run_state = RunState.FAILED
            self.job.status = JobStatus.COMPLETED

        finally:
            self.__save_job()
            self.job = None

    def __get_job(self):
        with self.db.session() as s:
            q = (
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
            )
            return s.exec(q).first()

    def __save_job(self):
        if not self.job:
            return
        with self.db.session() as s:
            job = s.get(Job, self.job.id)
            if not job:
                raise AppErrors.no_such_job
            current = self.job.model_dump(exclude_unset=True)
            for key, value in current.items():
                setattr(job, key, value)
            s.add(job)
            s.commit()
            s.refresh(job)
            self.job = job

    def __prepare_app(self):
        if not self.job:
            return
        with self.db.session() as s:
            novel = s.get(Novel, self.job.novel_id)
        if not novel:
            raise AppErrors.no_such_novel
        if not novel.title:
            raise AppErrors.no_novel_title
        if self.token != getattr(self.app, 'token'):
            self.__prepare_crawler()
            self.app.prepare_novel_output_path(novel.url, novel.title)
            metadata_list = list(load_all_metadata_from_path(self.app.output_path))
            if len(metadata_list) != 1:
                raise AppErrors.unable_to_resume_job
            update_session_from_metadata(self.app, metadata_list[0])

    def __prepare_crawler(self):
        if not self.job:
            return
        self.app.destroy()
        self.app.user_input = self.job.url
        self.app.output_path = self.ctx.config.app.output_path
        self.app.output_formats = {
            x: True
            for x in self.ctx.config.app.enabled_formats
        }
        self.app.initialize()
        self.app.prepare_search()

    def __fetch_novel(self):
        if not self.job:
            return

        crawler = self.app.crawler
        if not crawler:
            self.__prepare_crawler()
            assert crawler

        self.app.get_novel_info()
        self.app.chapters = crawler.chapters

        with self.db.session() as s:
            novel = s.get(Novel, self.job.novel_id)
            if not novel:
                raise AppErrors.no_such_novel

            novel.orphan = False
            novel.title = crawler.novel_title
            novel.cover = crawler.novel_cover
            novel.authors = crawler.novel_author
            novel.synopsis = crawler.novel_synopsis
            novel.tags = crawler.novel_tags
            novel.volume_count = len(crawler.volumes)
            novel.chapter_count = len(crawler.chapters)

            s.add(novel)
            s.commit()

    def __fetch_content(self):
        crawler = self.app.crawler
        if not crawler:

            self.__prepare_crawler()
            assert crawler

        self.app.start_download()

    def __bind_novel(self):
        self.app.bind_books()
        self.app.compress_books()

    def __create_artifact(self, format: OutputFormat, file: str):
        if not self.job:
            return
        if not self.job.novel_id:
            raise AppErrors.no_such_novel
        with self.db.session() as s:
            artifact = s.exec(
                select(Artifact)
                .where(Artifact.novel_id == self.job.novel_id)
                .where(Artifact.format == format)
            ).first()
            if not artifact:
                artifact = Artifact(
                    novel_id=self.job.novel_id,
                    output_file=file,
                    format=format,
                )
            else:
                artifact.output_file = file
            s.add(artifact)
            s.commit()
