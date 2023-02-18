import asyncio
import io
import os
import re
import shutil
import typing as t
import logging

from .utils import to_thread
from ...core.app import App
from ...core.sources import crawler_list, prepare_crawler
from ...core.crawler import Crawler
from ...utils.uploader import upload

logger = logging.getLogger(__name__)


@to_thread
def download_novel(app: App) -> list:
    try:
        app.pack_by_volume = False
        app.start_download()
        app.bind_books()
        app.compress_books()
        assert isinstance(app.archived_outputs, list)
        return app.archived_outputs
    except Exception as ex:
        logger.exception(ex)


@to_thread
def novel_by_url(url: str) -> App:
    app = App()
    app.user_input = url
    app.crawler = prepare_crawler(app.user_input)
    app.get_novel_info()
    assert isinstance(app.crawler, Crawler)
    return app


@to_thread
def novel_by_title(name: str, pattern: str) -> App:
    app = App()
    app.user_input = name.strip()
    app.crawler_links = [
        str(link)
        for link, crawler in crawler_list.items()
        if crawler.search_novel != Crawler.search_novel
        and (not pattern or re.search(pattern, link))
    ]

    app.search_novel()
    return app


@to_thread
def upload_file(archive: str) -> str | io.BufferedIOBase | None:
    # Check file size
    file_size = os.stat(archive).st_size
    if file_size >= 8388608:
        try:
            description = "Generated by: lncrawl Discord bot"
            return upload(archive, description)
        except Exception as e:
            logger.error("Failed to upload file: %s", archive, e)
            return None

    return open(archive, "rb")


@to_thread
def destroy_app(app: App):
    app.destroy()


def archive_metadata(archive) -> t.Tuple[str, str]:
    return os.path.basename(os.path.dirname(archive)), os.path.basename(archive)


async def update_progress(app: App, editFollowup: t.Callable[[str], None]):
    chapterCount = len(app.chapters)
    lastProgress = 0
    while app.crawler.future_progress < chapterCount:
        # this is shit, but it ensures we won't be stuck if we miss the done window
        if app.crawler.future_progress < lastProgress:
            break
        lastProgress = app.crawler.future_progress
        await editFollowup(f"Download in progress: {lastProgress}/{chapterCount}")
        await asyncio.sleep(1)
    # not cool, but we're risking this property to be reset by further downloads
    await editFollowup(f"Done: {chapterCount}/{chapterCount}. Uploading your file.")


def configure_output_path(app: App):
    # set output path
    root = os.path.abspath(".discord_bot_output")
    output_path = os.path.join(root, app.good_source_name, app.good_file_name)
    shutil.rmtree(output_path, ignore_errors=True)
    os.makedirs(output_path, exist_ok=True)
    return output_path
