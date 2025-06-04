"""
To download chapter images
"""

import logging
from concurrent.futures import Future
from pathlib import Path
from threading import Event
from typing import List

from ..utils.imgen import generate_cover_image

logger = logging.getLogger(__name__)


def fetch_chapter_images(app, signal=Event()):
    from .app import App
    assert isinstance(app, App) and app.crawler, 'Invalid app instance'

    def _fetch_content_image(url: str, image_file: Path):
        assert app.crawler
        img = app.crawler.download_image(url)
        image_file.parent.mkdir(parents=True, exist_ok=True)
        if img.mode not in ("L", "RGB", "YCbCr", "RGBX"):
            if img.mode == "RGBa":
                # RGBa -> RGB isn't supported so we go through RGBA first
                img.convert("RGBA").convert("RGB")
            else:
                img = img.convert("RGB")
        img.save(image_file.as_posix(), "JPEG", optimized=True)
        img.close()
        logger.debug("Saved image: %s", image_file)

    def _fetch_cover_image(cover_url: str):
        cover_file = Path(app.output_path) / "cover.jpg"
        try:
            _fetch_content_image(cover_url, cover_file)
        except Exception as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to download cover", e)
        try:
            if not cover_file.is_file():
                generate_cover_image(cover_file.as_posix())
        except Exception as e:
            if logger.isEnabledFor(logging.DEBUG):
                logger.exception("Failed to generate cover", e)
        app.book_cover = str(cover_file)

    # all tasks
    futures: List[Future] = []

    # download or generate cover
    if app.crawler.novel_cover:
        f = app.crawler.executor.submit(_fetch_cover_image, app.crawler.novel_cover)
        futures.append(f)

    # download content images
    image_folder = Path(app.output_path) / "images"
    for chapter in app.chapters:
        images = chapter.get("images") or {}
        for filename, url in images.items():
            image_file = image_folder / str(filename)
            if url and not image_file.is_file():
                f = app.crawler.executor.submit(_fetch_content_image, url, image_file)
                futures.append(f)

    if not futures:
        return

    # wait for download to finish
    current = 0
    app.fetch_images_progress = 0
    try:
        for _ in app.crawler.resolve_as_generator(
            futures,
            desc="  Images",
            unit="item",
            signal=signal,
        ):
            current += 1
            app.fetch_images_progress = 100 * current / len(futures)
            yield
    finally:
        logger.info(f"Downloaded {current} images")

    # discard failed images
    for chapter in app.chapters:
        images = chapter.get("images")
        if not images or not isinstance(images, dict):
            continue

        failed_images = []
        for filename, url in images.items():
            image_file = image_folder / str(filename)
            if not image_file.is_file():
                failed_images.append(filename)
        if not failed_images:
            continue

        soup = app.crawler.make_soup(chapter["body"])
        if not soup.body:
            continue

        for filename in failed_images:
            images.pop(filename)
            for img in soup.select(f'img[alt="{filename}"]'):
                img.extract()
        chapter["body"] = soup.body.decode_contents()
