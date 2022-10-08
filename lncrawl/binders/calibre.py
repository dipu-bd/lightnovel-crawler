import logging
import os
import subprocess

logger = logging.getLogger(__name__)

EBOOK_CONVERT = "ebook-convert"
CALIBRE_LINK = "https://calibre-ebook.com/download"


def run_ebook_convert(*args):
    """
    Calls `ebook-convert` with given args
    Visit https://manual.calibre-ebook.com/generated/en/ebook-convert.html for argument list.
    """
    try:
        isdebug = os.getenv("debug_mode")
        with open(os.devnull, "w", encoding="utf8") as dumper:
            subprocess.call(
                [EBOOK_CONVERT] + list(args),
                stdout=None if isdebug else dumper,
                stderr=None if isdebug else dumper,
            )

        return True
    except Exception:
        if logger.isEnabledFor(logging.DEBUG):
            logger.exception("Failed to convert ebook with args: %s", list(args))

        return False


def epub_to_calibre(app, epub_file, out_fmt):
    if not os.path.exists(epub_file):
        return None

    epub_path = os.path.dirname(epub_file)
    epub_file_name = os.path.basename(epub_file)
    file_name_without_ext = epub_file_name.replace(".epub", "")

    work_path = os.path.dirname(epub_path)
    out_path = os.path.join(work_path, out_fmt)
    out_file_name = file_name_without_ext + "." + out_fmt
    out_file = os.path.join(out_path, out_file_name)

    os.makedirs(out_path, exist_ok=True)

    logger.debug('Converting "%s" to "%s"', epub_file, out_file)

    args = [
        epub_file,
        out_file,
        "--unsmarten-punctuation",
        "--no-chapters-in-toc",
        "--title",
        file_name_without_ext,
        "--authors",
        app.crawler.novel_author,
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
    if out_fmt == "pdf":
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
        print("Created: %s" % out_file_name)
        return out_file
    else:
        logger.error("[%s] conversion failed: %s", out_fmt, epub_file_name)
        return None


def make_calibres(app, epubs, out_fmt):
    if out_fmt == "epub" or not epubs:
        return epubs

    if not run_ebook_convert("--version"):
        logger.error("Install Calibre to generate %s: %s", out_fmt, CALIBRE_LINK),
        return

    out_files = []
    for epub in epubs:
        out = epub_to_calibre(app, epub, out_fmt)
        out_files += [out]

    return out_files
