"""
To bind into ebooks
"""
import logging
import os
import shutil
import zipfile
from pathlib import Path
from typing import Generator, List

from ..models import OutputFormat

logger = logging.getLogger(__name__)

depends_on_none = [
    OutputFormat.json,
    OutputFormat.epub,
    OutputFormat.web,
    OutputFormat.text,
]
depends_on_epub = [
    OutputFormat.docx,
    OutputFormat.mobi,
    OutputFormat.pdf,
    OutputFormat.rtf,
    OutputFormat.azw3,
    OutputFormat.fb2,
    OutputFormat.lit,
    OutputFormat.lrf,
    OutputFormat.oeb,
    OutputFormat.pdb,
    OutputFormat.rb,
    OutputFormat.snb,
    OutputFormat.tcr,
]
available_formats = depends_on_none + depends_on_epub


def make_format(app, data, fmt: OutputFormat):
    from ..core.app import App
    assert isinstance(app, App) and app.crawler, 'App instance'

    logger.info(f"Generating {fmt}")
    try:
        if fmt == OutputFormat.json:
            from .json import make_jsons
            yield from make_jsons(app, data)
        if fmt == OutputFormat.text:
            from .text import make_texts
            yield from make_texts(app, data)
        elif fmt == OutputFormat.web:
            from .web import make_webs
            yield from make_webs(app, data)
        elif fmt == OutputFormat.epub:
            from .epub import make_epubs
            yield from make_epubs(app, data)
        elif fmt in depends_on_epub:
            from .calibre import make_calibres
            yield from make_calibres(app, fmt)
    except Exception as err:
        logger.exception('Failed to generate "%s": %s' % (fmt, err))


def create_archive(app, fmt: OutputFormat, files: List[str]):
    from ..core.app import App
    assert isinstance(app, App) and app.crawler, 'App instance'

    output_path = Path(app.output_path)
    archive_path = output_path / 'archives'
    os.makedirs(archive_path, exist_ok=True)

    if len(files) == 1 and Path(files[0]).is_file():
        logger.info(f"Not archiving single file for {fmt}")
        archive_file = archive_path / Path(files[0]).name
        shutil.copyfile(files[0], archive_file)
        return str(archive_file)

    first_id = app.chapters[0]["id"]
    last_id = app.chapters[-1]["id"]
    output_name = f"{app.good_file_name} c{first_id}-{last_id} ({fmt}).zip"
    archive_file = archive_path / output_name

    logger.info(f"Creating archive: {output_name}")
    with zipfile.ZipFile(archive_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        root_file = output_path / fmt
        for file in files:
            file_path = Path(file)
            if file_path.is_relative_to(root_file):
                arcname = file_path.relative_to(root_file).as_posix()
            elif file_path.is_relative_to(output_path):
                arcname = file_path.relative_to(output_path).as_posix()
            else:
                continue
            zipf.write(file, arcname)

    if archive_file.is_file():
        return str(archive_file)


def generate_books(app, data) -> Generator[OutputFormat, None, None]:
    from ..core.app import App
    assert isinstance(app, App) and app.crawler, 'App instance'

    enabled_formats = [
        fmt
        for fmt in available_formats
        if app.output_formats.get(fmt)
    ]

    app.binding_progress = 0
    app.generated_books = {}
    app.archived_outputs = []
    app.generated_archives = {}
    for i, fmt in enumerate(enabled_formats):
        files = list(make_format(app, data, fmt))
        if not files:
            logger.error(f"No output files for {fmt}")
            continue

        app.generated_books[fmt] = files
        logger.info(f"Generated {len(files)} files for {fmt}")

        archive_file = create_archive(app, fmt, files)
        if not archive_file:
            logger.error(f"No archive file for {fmt}")
            continue

        app.archived_outputs.append(archive_file)
        app.generated_archives[fmt] = archive_file
        app.binding_progress = 100 * (i + 1) / len(enabled_formats)

        yield fmt
