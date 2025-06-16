"""
To download chapter bodies
"""

import json
import logging
from pathlib import Path
from threading import Event
from typing import Dict

from ..models.chapter import Chapter
from .arguments import get_args

logger = logging.getLogger(__name__)


def get_chapter_file(
    chapter: Chapter,
    output_path: str,
    pack_by_volume: bool,
):
    dir_name = Path(output_path) / "json"
    if pack_by_volume:
        vol_name = "Volume " + str(chapter.volume).rjust(2, "0")
        dir_name = dir_name / vol_name

    chapter_name = str(chapter.id).rjust(5, "0")
    json_file = dir_name / (chapter_name + ".json")
    return json_file


def _save_chapter(file_name: Path, chapter: Chapter):
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
        chapter.body = "".join([title, chapter.body])

    file_name.parent.mkdir(parents=True, exist_ok=True)
    with file_name.open("w", encoding="utf-8") as fp:
        json.dump(chapter, fp, ensure_ascii=False)


def restore_chapter_body(app):
    from .app import App
    assert isinstance(app, App) and app.crawler, 'Invalid app instance'

    # attempt to restore from file cache
    restored = 0
    file_names: Dict[int, Path] = {}
    for chapter in app.chapters:
        file_name = get_chapter_file(
            chapter,
            pack_by_volume=app.pack_by_volume,
            output_path=app.output_path,
        )
        file_names[chapter.id] = file_name

        if not file_name.is_file():
            continue
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                old_chapter = json.load(file)
                chapter.update(**old_chapter)
                restored += 1
        except json.JSONDecodeError:
            logger.debug("Unable to decode JSON from the file: %s" % file_name)
        except Exception as e:
            logger.exception("An error occurred while reading the file:", e)

    logger.info(f"Restored {restored}/{len(app.chapters)} chapters")
    return file_names


def fetch_chapter_body(app, signal=Event()):
    from .app import App
    assert isinstance(app, App) and app.crawler, 'Invalid app instance'

    if not app.chapters:
        return

    # attempt to restore from file cache
    file_names = restore_chapter_body(app)

    # remaining chapters
    pending_chapters = [
        chapter for chapter in app.chapters
        if not chapter.success
    ]

    # download remaining
    current = len(app.chapters) - len(pending_chapters)
    app.fetch_chapter_progress = 100 * current / len(app.chapters)
    for chapter in app.crawler.download_chapters(pending_chapters, signal=signal):
        if chapter:
            file_path = file_names.get(chapter.id)
            if file_path:
                _save_chapter(file_path, chapter)
        current += 1
        app.fetch_chapter_progress = 100 * current / len(app.chapters)
        yield
    logger.info(f"Downloaded {len(pending_chapters)} chapters")
