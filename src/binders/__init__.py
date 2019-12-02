#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
import logging
import traceback

from .epub import make_epubs
from .web import make_webs
from .text import make_texts
from .calibre import make_calibres

logger = logging.Logger('BINDERS')

depends_on_none = [
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
    out_formats = app.output_formats
    if not out_formats:
        out_formats = {x: True for x in available_formats}
    # end if

    # Resolve formats to output maintaining dependencies
    after_epub = [x for x in depends_on_epub if out_formats[x]]
    need_epub = 'epub' if len(after_epub) else None
    after_any = [x for x in depends_on_none if out_formats[x] or x == need_epub]

    # Generate output files
    outputs = dict()
    for fmt in (after_any + after_epub):
        try:
            if fmt == 'text':
                outputs[fmt] = make_texts(app, data)
            elif fmt == 'web':
                outputs[fmt] = make_webs(app, data)
            elif fmt == 'epub':
                outputs[fmt] = make_epubs(app, data)
            else:
                outputs[fmt] = make_calibres(app, outputs['epub'], fmt)
            # end if
        except Exception as err:
            logger.exception('Failed to generate "%s": %s' % (fmt, err))
        # end try
    # end for

    return outputs
# end def
