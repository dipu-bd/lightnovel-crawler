"""
To bind into ebooks
"""
import logging
from typing import Generator, Tuple, List

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
    OutputFormat.txt,
    OutputFormat.azw3,
    OutputFormat.fb2,
    OutputFormat.lit,
    OutputFormat.lrf,
    OutputFormat.oeb,
    OutputFormat.pdb,
    OutputFormat.rb,
    OutputFormat.snb,
    OutputFormat.tcr,
    # OutputFormat.pml,
    # OutputFormat.html,
]
available_formats = depends_on_none + depends_on_epub


def generate_books(app, data) -> Generator[Tuple[OutputFormat, List[str]], None, None]:
    from ..core.app import App
    assert isinstance(app, App) and app.crawler, 'App instance'

    progress = 0
    app.binding_progress = 0
    for fmt in available_formats:
        try:
            if not app.output_formats.get(fmt):
                continue
            if fmt == OutputFormat.json:
                from .json import make_jsons
                yield fmt, list(make_jsons(app, data))
            if fmt == OutputFormat.text:
                from .text import make_texts
                yield fmt, list(make_texts(app, data))
            elif fmt == OutputFormat.web:
                from .web import make_webs
                yield fmt, list(make_webs(app, data))
            elif fmt == OutputFormat.epub:
                from .epub import make_epubs
                yield fmt, list(make_epubs(app, data))
            elif fmt in depends_on_epub:
                from .calibre import make_calibres
                yield fmt, list(make_calibres(app, fmt))
        except Exception as err:
            logger.exception('Failed to generate "%s": %s' % (fmt, err))
        finally:
            progress += 1
            app.binding_progress = 100 * progress / len(available_formats)
