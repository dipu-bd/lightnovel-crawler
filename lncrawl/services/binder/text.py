import logging
from pathlib import Path
from threading import Event
import zipfile

from ...context import ctx
from ...dao import Artifact, LanguageCode
from ...exceptions import AbortedException
from ...utils.html_tools import extract_text

logger = logging.getLogger(__name__)


def make_text(working_dir: Path, artifact: Artifact, signal=Event(), **kwargs) -> None:
    out_file = ctx.files.resolve(artifact.output_file)
    tmp_file = working_dir / out_file.name

    language = LanguageCode(artifact.language) if artifact.language else None
    novel = ctx.novels.get(artifact.novel_id, language)
    with zipfile.ZipFile(tmp_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        if signal.is_set():
            raise AbortedException()
        for volume in ctx.volumes.list(artifact.novel_id, language=language):
            if signal.is_set():
                raise AbortedException()
            for chapter in ctx.chapters.list(volume_id=volume.id, language=language):
                content: str = ""
                if language:
                    translation = ctx.chapters.get_chapter_translation(chapter, language)
                    if translation and translation.is_available:
                        content = ctx.files.load_text(translation.content_file)
                elif chapter.is_available:
                    content = ctx.files.load_text(chapter.content_file)

                if content:
                    content = chapter.title + "\n\n" + extract_text(content)
                    chapter_file = f"{volume.serial:03}/{chapter.serial:05}.txt"
                    zipf.writestr(chapter_file, content.encode())

        if signal.is_set():
            raise AbortedException()
        for image in ctx.images.list(novel_id=artifact.novel_id):
            if image.is_available:
                img_data = ctx.files.load(image.image_file)
                zipf.writestr(f"images/{image.id}.jpg", img_data)

        if signal.is_set():
            raise AbortedException()
        if novel.cover_available:
            img_data = ctx.files.load(novel.cover_file)
            zipf.writestr("cover.jpg", img_data)

        if signal.is_set():
            raise AbortedException()
        meta_text = "\n".join(
            [
                f"{novel.url}",
                "",
                "-" * 40,
                "",
                novel.title,
                f"by, {novel.authors}",
                "",
                "-" * 40,
                "",
                extract_text(novel.synopsis or ""),
                "",
                "-" * 40,
                "",
                f"Tags: {', '.join(map(lambda s: s.title(), novel.tags))}",
                f"Volumes: {novel.volume_count}",
                f"Chapters: {novel.chapter_count}",
            ]
        )
        zipf.writestr("meta.txt", meta_text.encode())

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.unlink(True)
    tmp_file.rename(out_file)
    logger.info(f"Created: {out_file}")
