import logging
import os
import subprocess
from typing import Generator

from lncrawl.models import OutputFormat

logger = logging.getLogger(__name__)
EBOOK_CONVERT = "ebook-convert"
CALIBRE_LINK = "https://calibre-ebook.com/download"


def run_ebook_convert(*args) -> bool:
    """
    Calls `ebook-convert` with given args
    Visit https://manual.calibre-ebook.com/generated/en/ebook-convert.html for argument list.
    """
    try:
        isdebug = os.getenv("debug_mode")
        with open(os.devnull, "w", encoding="utf8") as dumper:
            subprocess.run(
                args=[EBOOK_CONVERT] + list(args),
                stdout=None if isdebug else dumper,
                stderr=dumper,
                check=True
            )

        return True
    except subprocess.CalledProcessError:
        logger.exception("Failed to convert ebook with args: %s", list(args))
        return False
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", str(e))
        return False


def epub_to_calibre(app, epub_file: str, fmt: OutputFormat):
    from ..core.app import App
    assert isinstance(app, App) and app.crawler

    if not os.path.exists(epub_file):
        return

    epub_path = os.path.dirname(epub_file)
    epub_file_name = os.path.basename(epub_file)
    file_name_without_ext, _ = os.path.splitext(epub_file_name)

    work_path = os.path.dirname(epub_path)
    out_path = os.path.join(work_path, fmt)
    out_file_name = file_name_without_ext + "." + fmt
    out_file = os.path.join(out_path, out_file_name)
    os.makedirs(out_path, exist_ok=True)

    logger.info(f'Converting "{epub_file_name}" to "{out_file_name}"', )
    args = [
        epub_file,
        out_file,
        "--unsmarten-punctuation",
        "--no-chapters-in-toc",
        "--title",
        file_name_without_ext,
        "--authors",
        app.crawler.novel_author,
        "--comments",
        app.crawler.novel_synopsis,
        "--language",
        app.crawler.language,
        "--tags",
        ",".join(app.crawler.novel_tags),
        "--series",
        app.crawler.novel_title,
        "--publisher",
        app.crawler.home_url,
        "--book-producer",
        "Lightnovel Crawler",
        "--enable-heuristics",
        "--disable-renumber-headings",
    ]

    if app.book_cover:
        args += ["--cover", app.book_cover]
    if fmt == "pdf":
        args += [
            "--paper-size",
            "letter",
            "--pdf-page-numbers",
            "--pdf-hyphenate",
            "--pdf-header-template",
            '<p style="text-align:center; color:#555; font-size:0.9em">⦗ _TITLE_ &mdash; _SECTION_ ⦘</p>',
        ]

    run_ebook_convert(*args)
    if os.path.exists(out_file):
        logger.info("Created: %s", out_file_name)
        yield out_file
    else:
        logger.error("[%s] conversion failed: %s", fmt, epub_file_name)


def make_calibres(app, fmt: OutputFormat) -> Generator[str, None, None]:
    from ..core.app import App
    assert isinstance(app, App) and app.crawler

    epubs = app.generated_books.get(OutputFormat.epub)
    if not epubs:
        return

    if not run_ebook_convert("--version"):
        logger.error(f"Install Calibre to generate {fmt}: {CALIBRE_LINK}")
        return

    for epub in epubs:
        yield from epub_to_calibre(app, epub, fmt)
