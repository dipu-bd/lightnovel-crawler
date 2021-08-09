# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
import logging

from .epub import make_epubs
from .web import make_webs
from .text import make_texts
from .calibre import make_calibres

logger = logging.getLogger(__name__)

depends_on_none = [
    'json',
    'epub',
    'text',
    'web',
]
depends_on_epub = [
    'docx',
    'mobi',
    'pdf',
    'rtf',
    'txt',
    'azw3',
    'fb2',
    'lit',
    'lrf',
    'oeb',
    'pdb',
    'rb',
    'snb',
    'tcr',
    # 'pml',
    # 'html',
]
available_formats = depends_on_none + depends_on_epub


def generate_books(app, data):
    app.progress = 0
    out_formats = app.output_formats
    if not out_formats:
        out_formats = {}
    # end if
    out_formats = {x: out_formats.get(x, False) for x in available_formats}

    # Resolve formats to output maintaining dependencies
    after_epub = [x for x in depends_on_epub if out_formats[x]]
    need_epub = 'epub' if len(after_epub) else None
    after_any = [x for x in depends_on_none
                 if out_formats[x] or x == need_epub]
    formats_to_generate = after_any + after_epub

    # Generate output files
    progress = 0
    outputs = dict()
    for fmt in formats_to_generate:
        try:
            if fmt == 'text':
                outputs[fmt] = make_texts(app, data)
            elif fmt == 'web':
                outputs[fmt] = make_webs(app, data)
            elif fmt == 'epub':
                outputs[fmt] = make_epubs(app, data)
            elif fmt in depends_on_epub:
                outputs[fmt] = make_calibres(app, outputs['epub'], fmt)
            # end if
        except Exception as err:
            logger.exception('Failed to generate "%s": %s' % (fmt, err))
        finally:
            progress += 1
            app.progress = 100 * progress / len(formats_to_generate)
        # end try
    # end for

    return outputs
# end def
