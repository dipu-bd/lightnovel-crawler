"""
To bind into ebooks
"""
import logging
from typing import Dict, List

from ..models import OutputFormat

logger = logging.getLogger(__name__)

depends_on_none = [
    OutputFormat.json,
    OutputFormat.epub,
    OutputFormat.text,
    OutputFormat.web,
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


def generate_books(app, data):
    app.progress = 0
    out_formats = app.output_formats
    if not out_formats:
        out_formats = {}

    out_formats = {x: out_formats.get(x, False) for x in available_formats}

    # Resolve formats to output maintaining dependencies
    after_epub = [x for x in depends_on_epub if out_formats[x]]
    need_epub = "epub" if len(after_epub) else None
    after_any = [x for x in depends_on_none if out_formats[x] or x == need_epub]
    formats_to_generate = [x for x in after_any + after_epub]

    # Generate output files
    progress = 0
    outputs: Dict[OutputFormat, List[str]] = dict()
    for fmt in formats_to_generate:
        outputs[fmt] = []
        try:
            if fmt == OutputFormat.json:
                from .json import make_jsons
                outputs[fmt] += make_jsons(app, data)
            if fmt == OutputFormat.text:
                from .text import make_texts
                outputs[fmt] += make_texts(app, data)
            elif fmt == OutputFormat.web:
                from .web import make_webs
                outputs[fmt] += make_webs(app, data)
            elif fmt == OutputFormat.epub:
                from .epub import make_epubs
                outputs[fmt] += make_epubs(app, data)
            elif fmt in depends_on_epub:
                from .calibre import make_calibres
                outputs[fmt] += make_calibres(app, outputs[OutputFormat.epub], fmt)
        except Exception as err:
            logger.exception('Failed to generate "%s": %s' % (fmt, err))
        finally:
            progress += 1
            app.progress = 100 * progress / len(formats_to_generate)

    return outputs
