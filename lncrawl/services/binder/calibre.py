import logging
from pathlib import Path
import shlex
import subprocess
from threading import Event
from typing import Optional

from ...context import ctx
from ...dao import Artifact, LanguageCode, OutputFormat
from ...exceptions import AbortedException, ServerErrors
from ...utils.event_lock import EventLock

logger = logging.getLogger(__name__)

__lock = EventLock()
__is_available = None
__wait_timeout = 1


def __ebook_convert(*args, signal=Event()) -> bool:
    """
    Calls `ebook-convert` with given args
    Visit https://manual.calibre-ebook.com/generated/en/ebook-convert.html for argument list.
    """
    with (
        __lock.using(signal),
        subprocess.Popen(
            args=["ebook-convert"] + [str(a) for a in args],
            stderr=subprocess.STDOUT if ctx.logger.is_warn else subprocess.DEVNULL,
            stdout=subprocess.STDOUT if ctx.logger.is_debug else subprocess.DEVNULL,
        ) as p,
    ):
        logger.debug(shlex.join(p.args))  # type: ignore

        while p.poll() is None:
            if signal.is_set():
                p.terminate()
                p.kill()
                raise AbortedException()
            signal.wait(__wait_timeout)

        if p.poll() != 0:
            raise ServerErrors.ebook_convert_error

        return True


def is_calibre_available() -> bool:
    global __is_available
    if __is_available is None:
        try:
            __ebook_convert("--version")
            __is_available = True
        except Exception:
            __is_available = False
    return __is_available


def convert_epub(
    working_dir: Path,
    artifact: Artifact,
    signal=Event(),
    epub: Optional[Artifact] = None,
) -> None:
    out_file = ctx.files.resolve(artifact.output_file)
    tmp_file = working_dir / out_file.name
    if not epub:
        raise ServerErrors.no_epub_file

    language = LanguageCode(artifact.language) if artifact.language else None
    novel = ctx.novels.get(artifact.novel_id, language)
    epub_file = ctx.files.resolve(epub.output_file)

    if not is_calibre_available():
        raise ServerErrors.calibre_exe_not_found

    logger.info(
        f'Converting "{epub_file.name}" to "{out_file.name}"',
    )
    args = [
        epub_file,
        tmp_file,
        "--unsmarten-punctuation",
        "--no-chapters-in-toc",
        "--title",
        novel.title,
        "--authors",
        novel.authors,
        # "--comments",
        # novel.synopsis,
        "--language",
        artifact.language or novel.language,
        "--tags",
        ",".join(novel.tags),
        "--series",
        novel.title,
        "--publisher",
        novel.url,
        "--book-producer",
        "Lightnovel Crawler",
        "--enable-heuristics",
        "--disable-renumber-headings",
    ]

    if novel.cover_available:
        args += ["--cover", ctx.files.resolve(novel.cover_file)]
    if artifact.format == OutputFormat.pdf:
        args += [
            "--paper-size",
            "letter",
            "--pdf-page-numbers",
            "--pdf-hyphenate",
            "--pdf-header-template",
            '<p style="text-align:center; color:#555; font-size:0.9em">⦗ _TITLE_ &mdash; _SECTION_ ⦘</p>',
        ]

    __ebook_convert(*args, signal=signal)

    if not tmp_file.exists():
        raise ServerErrors.failed_creating_artifact

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.unlink(True)
    tmp_file.rename(out_file)
    logger.info("Created: %s", out_file.name)
