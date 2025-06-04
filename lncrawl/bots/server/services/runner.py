import logging
import os
import shutil
from pathlib import Path

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
from .tier import BATCH_DOWNLOAD_LIMIT, ENABLED_FORMATS


def microtask(sess: Session, job: Job) -> bool:
    app = App()
    ctx = ServerContext()
    logger = logging.getLogger(f'Job:{job.id}')

    try:
        #
        # Status: COMPLETED
        #
        if job.status == JobStatus.COMPLETED:
            logger.error('Job is already done')
            return False

        #
        # State: SUCCESS
        #
        if job.run_state == RunState.SUCCESS:
            job.status = JobStatus.COMPLETED
            sess.add(job)
            return True

        #
        # State: FAILED
        #
        if job.run_state == RunState.FAILED:
            job.status = JobStatus.COMPLETED
            logger.error(job.error)
            sess.add(job)
            return True

        #
        # State: PENDING
        #
        if job.status == JobStatus.PENDING:
            logger.info('Job started')
            job.status = JobStatus.RUNNING
            job.run_state = RunState.FETCHING_NOVEL
            sess.add(job)
            return True

        #
        # Prepare user, novel, app, crawler
        #
        user = job.user
        if not user:
            job.error = 'User is not available'
            logger.error(job.error)
            sess.add(job)
            return True

        novel = job.novel
        if not novel:
            job.error = 'Novel is not available'
            logger.error(job.error)
            sess.add(job)
            return True

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
            return True

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
            novel.tags = crawler.novel_tags
            novel.volume_count = len(crawler.volumes)
            novel.chapter_count = len(crawler.chapters)
            logger.info(f'Novel: {novel}')

            sess.add(novel)
            sess.add(job)
            return True

        #
        # Restore session
        #
        if novel.orphan or not novel.title:
            job.error = 'Failed to fetch novel'
            logger.error(job.error)
            sess.add(job)
            return True

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
            return True

        #
        # State: FETCHING_CHAPTERS
        #
        if job.run_state == RunState.FETCHING_CHAPTERS:
            app.chapters = crawler.chapters
            logger.info(f'Fetching ({len(app.chapters)} chapters)')

            batch_limit = BATCH_DOWNLOAD_LIMIT[user.tier]
            for i, chapter in enumerate(fetch_chapter_body(app)):
                if i == batch_limit:
                    break
            else:
                save_metadata(app)
                job.run_state = RunState.FETCHING_IMAGES
                logger.info('Fetch chapter completed')

            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')

            sess.add(job)
            return True

        app.chapters = crawler.chapters
        restore_chapter_body(app)

        # State: FETCHING_IMAGES
        #
        if job.run_state == RunState.FETCHING_IMAGES:
            logger.info(f'Fetching images from ({len(app.chapters)} chapters)')

            batch_limit = BATCH_DOWNLOAD_LIMIT[user.tier]
            for i, _ in enumerate(fetch_chapter_images(app)):
                if i == batch_limit:
                    break
            else:
                save_metadata(app)
                job.run_state = RunState.BINDING_NOVEL
                logger.info('Fetch image completed')

            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')

            sess.add(job)
            return True

        #
        # State: BINDING_NOVEL
        #
        if job.run_state == RunState.BINDING_NOVEL:
            logger.info('Binding novel')

            app.bind_books()
            app.compress_books()

            for fmt in OutputFormat:
                if str(fmt) == str(OutputFormat.json):
                    continue
                shutil.rmtree(
                    Path(app.output_path) / fmt,
                    ignore_errors=True,
                )

            job.run_state = RunState.PREPARE_ARTIFACTS
            job.progress = round(app.progress)
            logger.info(f'Current progress: {job.progress}%')
            sess.add(job)
            return True

        if not app.generated_archives:
            job.error = 'No archives available'
            logger.error(job.error)
            sess.add(job)
            return True

        #
        # State: PREPARE_ARTIFACTS
        #
        if job.run_state == RunState.PREPARE_ARTIFACTS:
            logger.info('Creating artifacts')

            for format, file in app.generated_archives.items():
                if not file:
                    continue
                artifact = sess.exec(
                    select(Artifact)
                    .where(Artifact.novel_id == job.novel_id)
                    .where(Artifact.format == format)
                ).first()
                if not artifact:
                    artifact = Artifact(
                        novel_id=novel.id,
                        output_file=file,
                        format=format,
                    )
                elif artifact.output_file != file:
                    if artifact.output_file and os.path.isfile(artifact.output_file):
                        os.remove(artifact.output_file)  # remove old file
                    artifact.output_file = file
                sess.add(artifact)

            logger.info('Success!')
            job.progress = 100
            job.run_state = RunState.SUCCESS
            sess.add(job)
            return True

    except Exception as e:
        logger.exception('Job failed')
        job.run_state = RunState.FAILED
        job.error = str(e)
        sess.add(job)
        return True

    finally:
        app.destroy()

    return False
