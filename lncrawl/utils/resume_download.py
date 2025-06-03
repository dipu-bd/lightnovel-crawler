import json
import logging
from pathlib import Path
from typing import Iterable

from .. import constants as C
from ..core.app import App
from ..core.crawler import Crawler
from ..core.exeptions import LNException
from ..core.sources import prepare_crawler
from ..models import MetaInfo

logger = logging.getLogger(__name__)


def load_all_metadata_from_path(output_path: str) -> Iterable[MetaInfo]:
    for meta_file in Path(output_path).glob("**/" + C.META_FILE_NAME):
        try:
            with open(meta_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                yield MetaInfo(**data)
        except Exception as e:
            logger.debug("Failed to read file %s | %s", meta_file, e)
    yield from ()


def update_session_from_metadata(app: App, meta: MetaInfo):
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
    app.crawler.language = meta.novel.language
    app.crawler.novel_synopsis = meta.novel.synopsis
    app.crawler.novel_tags = meta.novel.tags

    for k, v in meta.session.cookies.items():
        app.crawler.set_cookie(k, v)
    for k, v in meta.session.headers.items():
        app.crawler.set_header(k, v)
    app.crawler.scraper.proxies.update(meta.session.proxies)

    app.chapters = [
        chap
        for chap in app.crawler.chapters
        if chap.id in meta.session.download_chapters
    ]
    logger.info("Number of chapters to download: %d", len(app.chapters))
    logger.debug(app.chapters)

    return app
