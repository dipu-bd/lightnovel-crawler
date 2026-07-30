from functools import cache
import logging
from pathlib import Path
import shlex
import shutil
import subprocess
from threading import Event
from typing import List, Optional, Tuple

from ...assets.images import default_cover_image
from ...context import ctx
from ...dao import Artifact, LanguageCode, Novel, OutputFormat
from ...exceptions import AbortedException, ServerErrors

logger = logging.getLogger(__name__)

__is_available = None
__api_timeout = 600

# Filesystem-path flags rejected by the ebook-convert-api service.
_BLOCKED_FLAGS = {
    "cover",
    "debug-pipeline",
    "extract-to",
    "transform-css-rules",
}

# An ordered conversion option: (flag, value). A `None` value means a boolean flag.
Option = Tuple[str, Optional[str]]


@cache
def __calibre_exe_path() -> Optional[Path]:
    command = ctx.config.calibre.command
    exe_path = shutil.which(command)
    if not exe_path:
        return None
    path = Path(exe_path)
    if path.is_file():
        return path
    return path


def is_calibre_available() -> bool:
    """Whether any conversion backend (API service or local Calibre) is usable."""
    if ctx.config.calibre.api_enabled:
        return True
    return __calibre_exe_path() is not None


def __parse_option_string(value: str) -> List[Option]:
    """Parse a command-line option string into ordered (flag, value) pairs."""
    tokens = shlex.split(value)
    options: List[Option] = []
    index = 0
    while index < len(tokens):
        token = tokens[index]
        index += 1
        if not token.startswith("--"):
            continue
        flag = token[2:]
        if index < len(tokens) and not tokens[index].startswith("-"):
            options.append((flag, tokens[index]))
            index += 1
        else:
            options.append((flag, None))
    return options


def __build_options(artifact: Artifact, novel: Novel) -> List[Option]:
    """Build the ordered conversion options shared by both backends."""
    options: List[Option] = []
    options += [
        ("enable-heuristics", None),
        ("no-chapters-in-toc", None),
        ("unsmarten-punctuation", None),
        ("disable-renumber-headings", None),
    ]
    options += [
        ("title", novel.title),
        ("authors", novel.authors),
        ("tags", ",".join(novel.tags)),
        ("series", novel.title),
        ("publisher", novel.url),
        ("book-producer", "Lightnovel Crawler"),
    ]
    language = artifact.language or novel.language
    if language:
        options += [("language", language)]
    if artifact.format == OutputFormat.pdf:
        options += [
            ("paper-size", "letter"),
            ("pdf-page-numbers", None),
            ("pdf-hyphenate", None),
            (
                "pdf-header-template",
                '<p style="text-align:center; color:#555; font-size:0.9em">'
                "⦗ _TITLE_ &mdash; _SECTION_ ⦘</p>",
            ),
        ]
    return options


def __to_cli_args(options: List[Option]) -> List[str]:
    """Render options as `ebook-convert` command-line arguments."""
    args: List[str] = []
    for flag, value in options:
        args.append(f"--{flag}")
        if value is not None:
            args.append(value)
    return args


def __ebook_convert(
    epub_file: Path,
    tmp_file: Path,
    cli_args: list,
    signal: Event,
) -> None:
    """
    Calls `ebook-convert` with given args
    Visit https://manual.calibre-ebook.com/generated/en/ebook-convert.html for argument list.
    """
    exe_path = __calibre_exe_path()
    if not exe_path:
        raise ServerErrors.calibre_exe_not_found.with_extra(exe_path)

    cmd = [exe_path.as_posix(), epub_file, tmp_file] + cli_args
    cmd = list(map(str, cmd))
    logger.info(shlex.join(cmd))  # type: ignore
    with subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as p:
        while p.poll() is None:
            if signal.is_set():
                p.terminate()
                p.kill()
                raise AbortedException()
            signal.wait(0.1)
        if p.poll() != 0:
            stdout, stderr = p.communicate()
            msg = stderr or stdout or f"exit code {p.poll()}"
            raise ServerErrors.ebook_convert_error.with_extra(msg)


def __to_form_fields(options: List[Option]) -> dict:
    """Render options as ebook-convert-api form fields."""
    data: dict = {}
    for flag, value in options:
        if flag in _BLOCKED_FLAGS:
            continue
        name = flag.replace("-", "_")
        if value is None:
            data[name] = "true"
        else:
            data[name] = value
    return data


def __convert_via_api(
    epub_file: Path,
    tmp_file: Path,
    cover_file: Path,
    fields: dict,
    signal: Event,
) -> None:
    """Convert the EPUB using the remote ebook-convert-api service."""
    url = f"{ctx.config.calibre.api_url}/convert"
    with (
        open(epub_file, "rb") as fp,
        open(cover_file, "rb") as cp,
    ):
        resp = ctx.http.post(
            url,
            signal=signal,
            data=fields,
            files={
                "file": (epub_file.name, fp),
                "cover": (cover_file.name, cp),
            },
            timeout=__api_timeout,
        )
        if not resp.ok:
            # The body carries the API's reason (e.g. which form field failed a
            # 422 validation) — surface it instead of a bare status code.
            logger.warning(f"calibre-api {resp.status_code} for {url}: {resp.text}")
        resp.raise_for_status()
        tmp_file.write_bytes(resp.content)


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

    cfg = ctx.config.calibre
    if not is_calibre_available():
        raise ServerErrors.calibre_exe_not_found

    tmp_file.parent.mkdir(parents=True, exist_ok=True)
    logger.info(f'Converting "{epub_file.name}" to "{out_file.name}"')

    options = __build_options(artifact, novel)
    if novel.cover_available:
        cover_file = ctx.files.resolve(novel.cover_file)
    else:
        cover_file = default_cover_image()

    converted = False
    if cfg.api_enabled:
        try:
            fields = __to_form_fields(options)
            fields["output_format"] = str(artifact.format)
            __convert_via_api(epub_file, tmp_file, cover_file, fields, signal)
            converted = tmp_file.is_file()
        except AbortedException:
            raise
        except Exception as e:
            logger.warning(f"calibre-api conversion failed. {e!r}", exc_info=ctx.logger.is_debug)
            if not cfg.api_fallback_to_local:
                raise ServerErrors.ebook_convert_error from e

    if not converted:
        args = __to_cli_args(options)
        args += ["--cover", cover_file.as_posix()]
        __ebook_convert(epub_file, tmp_file, args, signal=signal)
        converted = tmp_file.is_file()

    if not converted:
        raise ServerErrors.failed_creating_artifact

    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.unlink(True)
    shutil.move(str(tmp_file), str(out_file))
    logger.info("Created: %s", out_file.name)
