"""
To download chapter bodies
"""
import base64
import hashlib
import json
import logging
import os
from io import BytesIO

from PIL import Image

from ..core.exeptions import LNException
from .arguments import get_args

logger = logging.getLogger(__name__)


def get_chapter_filename(app, chapter):
    from .app import App

    assert isinstance(app, App)

    dir_name = os.path.join(app.output_path, "json")
    if app.pack_by_volume:
        vol_name = "Volume " + str(chapter["volume"]).rjust(2, "0")
        dir_name = os.path.join(dir_name, vol_name)

    chapter_name = str(chapter["id"]).rjust(5, "0")
    return os.path.join(dir_name, chapter_name + ".json")


def extract_chapter_images(app, chapter):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None
    assert isinstance(chapter, dict), "Invalid chapter"

    if not chapter["body"]:
        return

    chapter.setdefault("images", {})
    soup = app.crawler.make_soup(chapter["body"])
    for img in soup.select("img"):
        if not img or not img.has_attr("src"):
            continue

        full_url = app.crawler.absolute_url(img["src"], page_url=chapter["url"])
        if not full_url.startswith("http"):
            continue

        filename = hashlib.md5(full_url.encode()).hexdigest() + ".jpg"
        img.attrs = {"src": "images/" + filename, "alt": filename}
        chapter["images"][filename] = full_url

    soup_body = soup.select_one("body")
    assert soup_body
    chapter["body"] = "".join([str(x) for x in soup_body.contents])


def save_chapter_body(app, chapter):
    from .app import App

    assert isinstance(app, App)

    file_name = get_chapter_filename(app, chapter)

    title = chapter["title"]
    title = "&lt;".join(title.split("<"))
    title = "&gt;".join(title.split(">"))

    if title not in chapter["body"]:
        chapter["body"] = "<h1>%s</h1>\n%s" % (title, chapter["body"])

    if get_args().add_source_url and chapter["url"] not in chapter["body"]:
        chapter["body"] += '<br><p>Source: <a href="%s">%s</a></p>' % (
            chapter["url"],
            chapter["url"],
        )

    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(json.dumps(chapter, ensure_ascii=False))


def download_chapter_body(app, chapter):
    assert isinstance(chapter, dict)
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    try:
        # Check previously downloaded chapter
        file_name = get_chapter_filename(app, chapter)
        if os.path.exists(file_name):
            logger.debug("Restoring from %s", file_name)
            with open(file_name, "r", encoding="utf-8") as file:
                old_chapter = json.load(file)

            chapter.update(**old_chapter)

        if chapter.get("body") and chapter.get("success", True):
            return

        # Fetch chapter body if it does not exists
        logger.debug("Downloading chapter %d: %s", chapter["id"], chapter["url"])
        chapter["body"] = app.crawler.download_chapter_body(chapter)
        extract_chapter_images(app, chapter)
        chapter["success"] = True
    except KeyboardInterrupt:
        raise LNException("Chapter download cancelled by user")
    except Exception as e:
        logger.debug("Failed", e)
        return f"[{chapter['id']}] Failed to get chapter body ({e.__class__.__name__}: {e})"
    finally:
        chapter["body"] = chapter.get("body") or ""
        save_chapter_body(app, chapter)
        app.progress += 1


def download_chapters(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    if not app.output_formats:
        app.output_formats = {}

    app.progress = 0
    futures = [
        app.crawler.executor.submit(
            download_chapter_body,
            app,
            chapter,
        )
        for chapter in app.chapters
    ]

    try:
        app.crawler.resolve_all(futures, desc="Chapters", unit="item")
    finally:
        logger.info("Processed %d chapters" % app.progress)


def download_image(app, url) -> Image.Image:
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    assert isinstance(url, str), "Invalid image url"
    if len(url) > 1000 or url.startswith("data:"):
        content = base64.b64decode(url.split("base64,")[-1])
    else:
        content = app.crawler.download_image(url)

    return Image.open(BytesIO(content))


def download_file_image(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    filename = os.path.join(app.output_path, "cover.jpg")

    if not os.path.isfile(filename):
        cover_urls = [
            app.crawler.novel_cover,
            "https://source.unsplash.com/featured/800x1032?abstract",
            # "https://picsum.photos/800/1032",
        ]
        for url in cover_urls:
            try:
                logger.info("Downloading cover image: %s", url)
                img = download_image(app, url)
                img.convert("RGB").save(filename, "JPEG")
                logger.debug("Saved cover: %s", filename)
                app.progress += 1
                break
            except KeyboardInterrupt:
                raise LNException("Cover download cancelled by user")
            except Exception as e:
                logger.debug("Failed to get cover: %s", url, e)

    if not os.path.isfile(filename):
        return f"[{filename}] Failed to download cover image"

    app.crawler.novel_cover = filename
    app.book_cover = filename


def download_content_image(app, url, filename, image_folder):
    from .app import App

    assert isinstance(app, App)
    image_file = os.path.join(image_folder, filename)
    try:
        if os.path.isfile(image_file):
            return

        img = download_image(app, url)
        os.makedirs(image_folder, exist_ok=True)
        with open(image_file, "wb") as f:
            img.convert("RGB").save(f, "JPEG")
            logger.debug("Saved image: %s", image_file)

    except KeyboardInterrupt:
        raise LNException("Image download cancelled by user")
    except Exception as e:
        return f"[{filename}] Failed to get content image: {url} | {e.__class__.__name__}: {e}"
    finally:
        app.progress += 1


def discard_failed_images(app, chapter, failed):
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


def download_chapter_images(app):
    from .app import App

    assert isinstance(app, App)
    assert app.crawler is not None

    # download or generate cover
    app.progress = 0
    futures = [
        app.crawler.executor.submit(
            download_file_image,
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
            download_content_image, app, url, filename, image_folder
        )
        for filename, url in images_to_download
    ]

    failed = []
    try:
        app.crawler.resolve_all(futures, desc="  Images", unit="item")
        failed = [
            filename
            for filename, url in images_to_download
            if not os.path.isfile(os.path.join(image_folder, filename))
        ]
    finally:
        logger.info("Processed %d images [%d failed]" % (app.progress, len(failed)))

    for chapter in app.chapters:
        discard_failed_images(app, chapter, failed)
