import json
import logging
from pathlib import Path
from typing import Iterable

from .. import constants as C
from ..models import Chapter, MetaInfo, Novel, Session
from .sources import prepare_crawler

logger = logging.getLogger(__name__)


def get_metadata_list(output_path: str) -> Iterable[MetaInfo]:
    for meta_file in Path(output_path).glob("**/" + C.META_FILE_NAME):
        try:
            with open(meta_file, "r", encoding="utf-8") as fp:
                data = json.load(fp)
                yield MetaInfo(**data)
        except Exception as e:
            logger.debug("Failed to read file %s | %s", meta_file, e)
    yield from ()


def save_metadata(app, completed=False):
    from .app import App
    if not isinstance(app, App) or not app.crawler:
        return

    novel = MetaInfo(
        session=Session(
            completed=completed,
            user_input=app.user_input or '',
            login_data=app.login_data,
            output_path=app.output_path or '',
            output_formats=app.output_formats,
            book_cover=app.book_cover,
            pack_by_volume=app.pack_by_volume,
            good_file_name=app.good_file_name,
            no_append_after_filename=app.no_suffix_after_filename,
            chapters_to_download=[chap.id for chap in app.chapters],
            proxies=dict(app.crawler.scraper.proxies),
            # generated_books=dict(app.generated_books),
            generated_archives=dict(app.generated_archives),
            search_progress=app.search_progress,
            fetch_novel_progress=app.fetch_novel_progress,
            fetch_content_progress=app.fetch_chapter_progress,
            fetch_images_progress=app.fetch_images_progress,
            binding_progress=app.binding_progress,
            cookies={
                k: v for k, v in app.crawler.cookies.items() if v
            },
            headers={
                k: (v if isinstance(v, str) else bytes(v).decode())
                for k, v in app.crawler.headers.items()
            },
        ),
        novel=Novel(
            url=app.crawler.novel_url,
            title=app.crawler.novel_title,
            authors=[x.strip() for x in app.crawler.novel_author.split(",")],
            cover_url=app.crawler.novel_cover,
            synopsis=app.crawler.novel_synopsis,
            language=app.crawler.language,
            tags=app.crawler.novel_tags,
            volumes=app.crawler.volumes,
            chapters=[Chapter.without_body(chap) for chap in app.crawler.chapters],
            is_rtl=app.crawler.is_rtl,
        ),
    )

    try:
        Path(app.output_path).mkdir(parents=True, exist_ok=True)
        file_name = Path(app.output_path) / C.META_FILE_NAME
        novel.to_json(file_name, encoding="utf-8", indent=2)
    except Exception:
        pass


def load_metadata(app, meta: MetaInfo):
    from .app import App
    novel = meta.novel
    session = meta.session
    if not (isinstance(app, App) and novel and session):
        return

    app.output_path = session.output_path
    app.user_input = session.user_input
    app.book_cover = session.book_cover
    app.login_data = session.login_data
    app.pack_by_volume = session.pack_by_volume
    app.output_formats = session.output_formats
    app.good_file_name = session.good_file_name
    app.no_suffix_after_filename = session.no_append_after_filename
    # app.generated_books = session.generated_books
    app.generated_archives = session.generated_archives
    app.search_progress = session.search_progress
    app.fetch_novel_progress = session.fetch_novel_progress
    app.fetch_chapter_progress = session.fetch_content_progress
    app.fetch_images_progress = session.fetch_images_progress
    app.binding_progress = session.binding_progress

    logger.info("Novel Url: %s", novel.url)
    if not app.crawler:
        app.crawler = prepare_crawler(novel.url)

    app.crawler.novel_title = novel.title
    app.crawler.novel_author = ", ".join(novel.authors)
    app.crawler.novel_cover = novel.cover_url
    app.crawler.volumes = novel.volumes
    app.crawler.chapters = novel.chapters
    app.crawler.is_rtl = novel.is_rtl
    app.crawler.language = novel.language
    app.crawler.novel_synopsis = novel.synopsis
    app.crawler.novel_tags = novel.tags

    for k, v in session.cookies.items():
        app.crawler.set_cookie(k, v)
    for k, v in session.headers.items():
        app.crawler.set_header(k, v)
    app.crawler.scraper.proxies.update(session.proxies)

    app.chapters = [
        chap
        for chap in app.crawler.chapters
        if chap.id in session.chapters_to_download
    ]
    logger.info("Number of chapters to download: %d", len(app.chapters))
    logger.debug(app.chapters)

    return app
