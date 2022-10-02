import json
import logging
from pathlib import Path
from typing import List

from box import Box
from questionary import prompt

from ... import constants as C
from ...core import display
from ...core.app import App
from ...core.arguments import get_args
from ...core.crawler import Crawler
from ...core.exeptions import LNException
from ...core.sources import prepare_crawler
from ...models import MetaInfo
from .open_folder_prompt import display_open_folder

logger = logging.getLogger(__name__)


def resume_session():
    args = get_args()
    output_path = args.resume or C.DEFAULT_OUTPUT_PATH

    resumable_meta_data: List[MetaInfo] = []
    for meta_file in Path(output_path).glob("**/" + C.META_FILE_NAME):
        try:
            with open(meta_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                meta: MetaInfo = Box(**data)
            if meta.novel and meta.session and not meta.session.completed:
                resumable_meta_data.append(meta)
        except Exception as e:
            logger.debug("Failed to read file %s | %s", meta_file, e)

    meta: MetaInfo = None
    if len(resumable_meta_data) == 1:
        meta = resumable_meta_data[0]
    elif len(resumable_meta_data) > 1:
        answer = prompt(
            [
                {
                    "type": "list",
                    "name": "resume",
                    "message": "Which one do you want to resume?",
                    "choices": display.format_resume_choices(resumable_meta_data),
                }
            ]
        )
        index = int(answer["resume"].split(".")[0])
        meta = resumable_meta_data[index - 1]

    if not meta:
        print("No unfinished download to resume\n")
        display.app_complete()
        return

    app = load_session_from_metadata(meta)
    assert isinstance(app.crawler, Crawler)

    print("Resuming", app.crawler.novel_title)
    print("Output path:", app.output_path)

    app.initialize()
    app.crawler.initialize()

    if app.can_do("login") and app.login_data:
        logger.debug("Login with %s", app.login_data)
        app.crawler.login(*list(app.login_data))

    app.start_download()
    app.bind_books()
    app.compress_books()
    app.destroy()
    display.app_complete()
    display_open_folder(app.output_path)


def load_session_from_metadata(meta: MetaInfo) -> App:
    app = App()
    assert meta.novel, "MetaInfo Novel is empty"
    assert meta.session, "MetaInfo Session is empty"

    app.output_path = meta.session.output_path
    app.user_input = meta.session.user_input
    app.login_data = meta.session.login_data
    app.pack_by_volume = meta.session.pack_by_volume
    app.output_formats = meta.session.output_formats
    app.good_file_name = meta.session.good_file_name
    app.no_suffix_after_filename = meta.session.no_append_after_filename
    logger.info("Novel Url: %s", meta.novel.url)

    app.crawler = prepare_crawler(meta.novel.url)
    if not isinstance(app.crawler, Crawler):
        raise LNException("No crawler found for " + meta.novel.url)

    app.crawler.novel_title = meta.novel.title
    app.crawler.novel_author = ", ".join(meta.novel.authors)
    app.crawler.novel_cover = meta.novel.cover_url
    app.crawler.volumes = meta.novel.volumes
    app.crawler.chapters = meta.novel.chapters
    app.crawler.is_rtl = meta.novel.is_rtl

    for k, v in meta.session.cookies.items():
        app.crawler.set_cookie(k, v)
    for k, v in meta.session.headers.items():
        app.crawler.set_header(k, v)
    app.crawler.scraper.proxies = meta.session.proxies

    app.chapters = [
        chap
        for chap in app.crawler.chapters
        if chap.id in meta.session.download_chapters
    ]
    logger.info("Number of chapters to download: %d", len(app.chapters))
    logger.debug(app.chapters)

    return app
