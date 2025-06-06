import logging
import os
import shutil
import time
import uuid
from pathlib import Path
from threading import Event

from sqlmodel import Session, select

from lncrawl.core.app import App
from lncrawl.core.download_chapters import (fetch_chapter_body,
                                            restore_chapter_body)
from lncrawl.core.download_images import fetch_chapter_images
from lncrawl.core.metadata import (get_metadata_list, load_metadata,
                                   save_metadata)
from lncrawl.models import OutputFormat

from ..context import ServerContext
from ..models.job import Artifact, Job, JobStatus, RunState
from .tier import ENABLED_FORMATS, SLOT_TIMEOUT_IN_SECOND

__runner_id = uuid.uuid4()


def microtask(sess: Session, job: Job, signal=Event()) -> None:
    app = App()
    ctx = ServerContext()
    logger = logging.getLogger(f'Job:{job.id}')

    try:
        #
        # Status: COMPLETED
        #
        if job.status == JobStatus.COMPLETED:
            logger.error('Job is already done')
            return

        #
        # State: SUCCESS
        #
        if job.run_state == RunState.SUCCESS:
            job.status = JobStatus.COMPLETED
            sess.add(job)
            return

        #
        # State: FAILED
        #
        if job.run_state == RunState.FAILED:
            job.status = JobStatus.COMPLETED
            logger.error(job.error)
            sess.add(job)
            return

        #
        # State: CANCELED
        #
        if job.run_state == RunState.CANCELED:
            job.status = JobStatus.COMPLETED
            logger.error(job.error)
            sess.add(job)
            return
        #
        # State: PENDING
        #
        if job.status == JobStatus.PENDING:
            logger.info('Job started')
            job.status = JobStatus.RUNNING
            job.run_state = RunState.FETCHING_NOVEL
            sess.add(job)
            return

        #
        # Prepare user, novel, app, crawler
        #
        user = job.user
        if not user:
            job.error = 'User is not available'
            logger.error(job.error)
            sess.add(job)
            return

        novel = job.novel
        if not novel:
            job.error = 'Novel is not available'
            logger.error(job.error)
            sess.add(job)
            return

        if novel.orphan:
            job.run_state = RunState.FETCHING_NOVEL

        app.user_input = novel.url
        app.output_path = ctx.config.app.output_path
        os.makedirs(app.output_path, exist_ok=True)
        app.output_formats = {x: True for x in ENABLED_FORMATS[user.tier]}
        app.output_formats[OutputFormat.json] = True
        app.prepare_search()

        crawler = app.crawler
        if not crawler:
            job.error = 'No crawler available for this novel'
            logger.error(job.error)
            sess.add(job)
            return

        #
        # State: FETCHING_NOVEL
        #
        if job.run_state == RunState.FETCHING_NOVEL:
            logger.info('Fetching novel info')
            app.get_novel_info()

            job.run_state = RunState.FETCHING_CHAPTERS
            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')

            novel.orphan = False
            novel.title = crawler.novel_title
            novel.cover = crawler.novel_cover
            novel.authors = crawler.novel_author
            novel.synopsis = crawler.novel_synopsis
            novel.tags = crawler.novel_tags or []
            novel.volume_count = len(crawler.volumes)
            novel.chapter_count = len(crawler.chapters)
            logger.info(f'Novel: {novel}')

            sess.add(novel)
            sess.add(job)
            return

        #
        # Restore session
        #
        if novel.orphan or not novel.title:
            job.error = 'Failed to fetch novel'
            logger.error(job.error)
            sess.add(job)
            return

        crawler.novel_url = novel.url
        crawler.novel_title = novel.title
        app.prepare_novel_output_path()
        logger.info(f'Checking metadata file: {app.output_path}')
        for meta in get_metadata_list(app.output_path):
            if meta.novel and meta.session and meta.novel.url == novel.url:
                logger.info('Loading session from metadata')
                load_metadata(app, meta)
                break
        else:
            job.error = 'Failed to restore metadata'
            logger.error(job.error)
            sess.add(job)
            return

        #
        # State: FETCHING_CHAPTERS
        #
        if job.run_state == RunState.FETCHING_CHAPTERS:
            app.chapters = crawler.chapters
            logger.info(f'Fetching ({len(app.chapters)} chapters)')

            last_report = 0.0
            start_time = time.time()
            timeout = SLOT_TIMEOUT_IN_SECOND[user.tier]
            for _ in fetch_chapter_body(app, signal):
                cur_time = time.time()
                if cur_time - start_time > timeout:
                    break
                if cur_time - last_report > 10:
                    last_report = cur_time
                    job.progress = round(app.progress)
                    sess.add(job)
                    sess.commit()
                    sess.refresh(job)
            else:
                save_metadata(app)
                if not signal.is_set():
                    job.run_state = RunState.FETCHING_IMAGES
                    logger.info('Fetch chapter completed')

            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')

            sess.add(job)
            return

        app.chapters = crawler.chapters
        restore_chapter_body(app)

        #
        # State: FETCHING_IMAGES
        #
        if job.run_state == RunState.FETCHING_IMAGES:
            logger.info(f'Fetching images from ({len(app.chapters)} chapters)')

            last_report = 0.0
            start_time = time.time()
            timeout = SLOT_TIMEOUT_IN_SECOND[user.tier]
            for _ in fetch_chapter_images(app, signal):
                cur_time = time.time()
                if cur_time - start_time > timeout:
                    break
                if cur_time - last_report > 10:
                    last_report = cur_time
                    job.progress = round(app.progress)
                    sess.add(job)
                    sess.commit()
                    sess.refresh(job)
            else:
                save_metadata(app)
                if not signal.is_set():
                    job.run_state = RunState.CREATING_ARTIFACTS
                    logger.info('Fetch image completed')

            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')

            sess.add(job)
            return

        #
        # State: CREATING_ARTIFACTS
        #
        if job.run_state == RunState.CREATING_ARTIFACTS:
            logger.info('Creating artifacts')

            for fmt, archive_file in app.bind_books(signal):
                # save progress
                job.progress = round(app.progress)
                sess.add(job)
                sess.commit()
                sess.refresh(job)

                # create or update artifact entry
                artifact = sess.exec(
                    select(Artifact)
                    .where(Artifact.novel_id == job.novel_id)
                    .where(Artifact.format == fmt)
                ).first()
                if not artifact:
                    artifact = Artifact(
                        format=fmt,
                        novel_id=novel.id,
                        output_file=archive_file,
                        file_name=os.path.basename(archive_file),
                    )
                else:
                    if (
                        artifact.output_file
                        and artifact.output_file != archive_file
                        and os.path.isfile(artifact.output_file)
                    ):  # remove old file
                        os.remove(artifact.output_file)
                    artifact.output_file = archive_file
                sess.add(artifact)
                sess.commit()

            # remove output folders (except json)
            for fmt in OutputFormat:
                if str(fmt) != str(OutputFormat.json):
                    output = Path(app.output_path) / fmt
                    shutil.rmtree(output, ignore_errors=True)

            logger.info('Success!')
            job.progress = round(app.progress)
            job.run_state = RunState.SUCCESS
            sess.add(job)
            return

    except Exception as e:
        logger.exception('Job failed')
        job.run_state = RunState.FAILED
        job.error = str(e)
        sess.add(job)

    finally:
        sess.commit()
        app.destroy()
