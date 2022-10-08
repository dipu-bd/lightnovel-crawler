"""
To download chapter bodies
"""
import json
import logging
import os

from ..models.chapter import Chapter
from ..utils.imgen import generate_cover_image
from .arguments import get_args

logger = logging.getLogger(__name__)


def _chapter_file(
    chapter: Chapter,
    output_path: str,
    pack_by_volume: bool,
):
    dir_name = os.path.join(output_path, "json")
    if pack_by_volume:
        vol_name = "Volume " + str(chapter.volume).rjust(2, "0")
        dir_name = os.path.join(dir_name, vol_name)

    chapter_name = str(chapter.id).rjust(5, "0")
    json_file = os.path.join(dir_name, chapter_name + ".json")
    return json_file


def _save_chapter(app, chapter: Chapter):
    from .app import App

    assert isinstance(app, App)

    if not chapter.body:
        chapter.body = "<p><i>Failed to download chapter body</i></p>"

    args = get_args()
    source_notice = (
        f'<br><p><small>Source: <a href="{chapter.url}">{chapter.url}</a></small></p>'
    )
    if args.add_source_url and not chapter.body.endswith(source_notice):
        chapter.body += source_notice

    title = chapter.title
    title = "&lt;".join(title.split("<"))
    title = "&gt;".join(title.split(">"))
    title = f"<h1>{title}</h1>"
    if not chapter.body.startswith(title):
        chapter.body = title + chapter.body

    file_name = _chapter_file(
        chapter,
        output_path=app.output_path,
        pack_by_volume=app.pack_by_volume,
    )
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as fp:
        json.dump(chapter, fp, ensure_ascii=False)


def fetch_chapter_body(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    if not app.output_formats:
        app.output_formats = {}

    # restore from file cache
    for chapter in app.chapters:
        file_name = _chapter_file(
            chapter,
            pack_by_volume=app.pack_by_volume,
            output_path=app.output_path,
        )
        if not os.path.exists(file_name):
            continue
        with open(file_name, "r", encoding="utf-8") as file:
            old_chapter = json.load(file)
            chapter.update(**old_chapter)
        if chapter.success:
            logger.debug(f"Restored chapter {chapter.id} from {file_name}")

    # downlaod remaining chapters
    app.progress = 0
    for progress in app.crawler.download_chapters(app.chapters):
        app.progress += progress

    for chapter in app.chapters:
        _save_chapter(app, chapter)

    logger.info(f"Processed {len(app.chapters)} chapters [{app.progress} fetched]")


def _fetch_content_image(app, url, image_file):
    from .app import App

    assert isinstance(app, App)

    if url and not os.path.isfile(image_file):
        try:
            img = app.crawler.download_image(url)
            os.makedirs(os.path.dirname(image_file), exist_ok=True)
            img.convert("RGB").save(image_file, "JPEG")
            logger.debug("Saved image: %s", image_file)
        finally:
            app.progress += 1


def _fetch_cover_image(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    filename = "cover.jpg"
    cover_file = os.path.join(app.output_path, filename)
    if app.crawler.novel_cover:
        try:
            _fetch_content_image(
                app,
                app.crawler.novel_cover,
                cover_file,
            )
        except Exception as e:
            logger.exception("Failed to download cover", e)

    if not os.path.isfile(cover_file):
        try:
            generate_cover_image(cover_file)
        except Exception as e:
            logger.exception("Failed to generate cover", e)

    app.progress += 1
    app.book_cover = cover_file
    assert os.path.isfile(app.book_cover), "Failed to download or generate cover image"


def _discard_failed_images(app, chapter, failed):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None
    assert isinstance(chapter, dict), "Invalid chapter"

    if not chapter["body"] or "images" not in chapter:
        return

    assert isinstance(chapter["images"], dict)
    current_failed = [filename for filename in failed if filename in chapter["images"]]
    if not current_failed:
        return

    soup = app.crawler.make_soup(chapter["body"])
    for filename in current_failed:
        chapter["images"].pop(filename)
        for img in soup.select(f'img[alt="{filename}"]'):
            img.extract()

    soup_body = soup.select_one("body")
    assert soup_body
    chapter["body"] = "".join([str(x) for x in soup_body.contents])


def fetch_chapter_images(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    # download or generate cover
    app.progress = 0
    futures = [
        app.crawler.executor.submit(
            _fetch_cover_image,
            app,
        )
    ]

    # download content images
    image_folder = os.path.join(app.output_path, "images")
    images_to_download = set(
        [
            (filename, url)
            for chapter in app.chapters
            for filename, url in chapter.get("images", {}).items()
        ]
    )
    futures += [
        app.crawler.executor.submit(
            _fetch_content_image,
            app,
            url,
            os.path.join(image_folder, filename),
        )
        for filename, url in images_to_download
    ]

    failed = []
    try:
        app.crawler.resolve_futures(futures, desc="  Images", unit="item")
        failed = [
            filename
            for filename, url in images_to_download
            if not os.path.isfile(os.path.join(image_folder, filename))
        ]
    finally:
        logger.info("Processed %d images [%d failed]" % (app.progress, len(failed)))

    for chapter in app.chapters:
        _discard_failed_images(app, chapter, failed)
