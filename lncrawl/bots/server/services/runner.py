import logging
import shutil
import time
from pathlib import Path
from threading import Event

from lncrawl.core.app import App
from lncrawl.core.download_chapters import restore_chapter_body
from lncrawl.core.metadata import (get_metadata_list, load_metadata,
                                   save_metadata)
from lncrawl.models import OutputFormat

from ..context import ServerContext
from ..models.enums import JobStatus, RunState
from ..models.job import Job
from ..models.novel import Artifact, Novel
from ..models.user import User
from .tier import ENABLED_FORMATS, SLOT_TIMEOUT_IN_SECOND


def microtask(job_id: str, signal=Event()) -> None:
    app = App()
    ctx = ServerContext()
    sess = ctx.db.session()
    job = sess.get_one(Job, job_id)
    logger = logging.getLogger(f'Job:{job_id}')

    def save(refresh=False):
        sess.add(job)
        sess.commit()
        if refresh:
            sess.refresh(job)

    logger.info('=== Task begin ===')
    try:
        #
        # Status: COMPLETED
        #
        if job.status == JobStatus.COMPLETED:
            logger.error('Job is already done')
            return save()

        #
        # State: SUCCESS, FAILED, CANCELED
        #
        if job.run_state in [
            RunState.FAILED,
            RunState.SUCCESS,
            RunState.CANCELED
        ]:
            job.status = JobStatus.COMPLETED
            return save()

        # State: PENDING
        #
        if job.status == JobStatus.PENDING:
            job.run_state = RunState.FETCHING_NOVEL
            job.status = JobStatus.RUNNING
            logger.info('Job started')
            return save()

        #
        # Prepare user, novel, app, crawler
        #
        user = sess.get(User, job.user_id)
        if not user:
            job.error = 'User is not available'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.FAILED
            return save()

        novel = sess.get(Novel, job.novel_id)
        if not novel:
            job.error = 'Novel is not available'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.FAILED
            return save()

        app.user_input = job.url
        app.output_formats = {x: True for x in ENABLED_FORMATS[user.tier]}
        app.output_formats[OutputFormat.json] = True
        app.prepare_search()
        crawler = app.crawler
        if not crawler:
            job.error = 'No crawler available for this novel'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.FAILED
            return save()

        #
        # State: FETCHING_NOVEL
        #
        if job.run_state == RunState.FETCHING_NOVEL:
            logger.info('Fetching novel info')

            app.get_novel_info()

            job.progress = round(app.progress)
            job.run_state = RunState.FETCHING_CONTENT

            novel.orphan = False
            novel.title = crawler.novel_title
            novel.cover = crawler.novel_cover
            novel.authors = crawler.novel_author
            novel.synopsis = crawler.novel_synopsis
            novel.tags = crawler.novel_tags or []
            novel.volume_count = len(crawler.volumes)
            novel.chapter_count = len(crawler.chapters)
            sess.add(novel)

            logger.info(f'Novel: {novel}')
            return save()

        #
        # Restore session
        #
        if novel.orphan or not novel.title:
            job.error = 'Failed to fetch novel'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.FAILED
            return save()

        crawler.novel_url = novel.url
        crawler.novel_title = novel.title
        app.prepare_novel_output_path()

        logger.info(f'Checking metadata file: {app.output_path}')
        for meta in get_metadata_list(app.output_path):
            if meta.novel and meta.session and meta.novel.url == novel.url:
                logger.info('Loading session from metadata')
                load_metadata(app, meta)
                break  # found matching metadata
        else:
            # did not find any matching metadata
            job.error = 'Failed to restore metadata'
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.FAILED
            return save()

        sess.refresh(novel)
        novel.extra = dict(novel.extra)
        novel.extra['output_path'] = app.output_path
        sess.add(novel)
        sess.commit()

        #
        # State: FETCHING_CONTENT
        #
        if job.run_state == RunState.FETCHING_CONTENT:
            app.chapters = crawler.chapters
            logger.info(f'Fetching ({len(app.chapters)} chapters)')

            done = False
            last_report = 0.0
            start_time = time.time()
            timeout = SLOT_TIMEOUT_IN_SECOND[user.tier]
            for _ in app.start_download(signal):
                cur_time = time.time()
                if cur_time - start_time > timeout:
                    break
                if job.progress > round(app.progress):
                    logger.info('Failed to fetch some content')
                    done = True
                    break
                if cur_time - last_report > 5:
                    job.progress = round(app.progress)
                    last_report = cur_time
                    save(refresh=True)
            else:
                done = True

            if done:
                app.fetch_chapter_progress = 100
                app.fetch_images_progress = 100
                save_metadata(app)
                if not signal.is_set():
                    logger.info('Fetch content completed')
                    job.run_state = RunState.CREATING_ARTIFACTS

            job.progress = round(app.progress)
            return save()

        app.chapters = crawler.chapters
        restore_chapter_body(app)

        #
        # State: CREATING_ARTIFACTS
        #
        if job.run_state == RunState.CREATING_ARTIFACTS:
            logger.info('Creating artifacts')
            for fmt, archive_file in app.bind_books(signal):
                job.progress = round(app.progress)
                save(refresh=True)
                artifact = Artifact(
                    format=fmt,
                    job_id=job.id,
                    novel_id=novel.id,
                    output_file=archive_file,
                )
                ctx.artifacts.upsert(artifact)

            # remove output folders (except json)
            for fmt in OutputFormat:
                if str(fmt) != str(OutputFormat.json):
                    output = Path(app.output_path) / fmt
                    shutil.rmtree(output, ignore_errors=True)

            logger.info('Success!')
            job.progress = 100
            job.status = JobStatus.COMPLETED
            job.run_state = RunState.SUCCESS
            save()

            if ctx.users.is_verified(user.email):
                try:
                    detail = ctx.jobs.get(job_id)
                    ctx.mail.send_job_success(user.email, detail)
                    logger.error(f'Success report was sent to <{user.email}>')
                except Exception as e:
                    logger.error('Failed to email success report', e)

    except Exception as e:
        logger.exception('Job failed')
        job.status = JobStatus.COMPLETED
        job.run_state = RunState.FAILED
        job.error = str(e)
        return save()

    finally:
        sess.close()
        logger.info('=== Task end ===')
