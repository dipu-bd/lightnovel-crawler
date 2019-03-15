#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
import logging

from .epub import make_epubs
from .html import make_htmls
from .mobi import make_mobis
from .text import make_texts
from .docx import make_docx
from .pdf import make_pdfs

logger = logging.Logger('BINDERS')

available_formats = [
    'epub',
    'mobi',
    'html',
    'text',
    'docx',
    'pdf',
]


def process(fn, app, inp, fmt):
    try:
        return fn(app, inp)
    except Exception:
        logger.info('Failed to generate *.%s files' % fmt)
        import traceback        
        logger.debug(traceback.format_exc())
        return None
    # end try
# end def


def bind_books(app, data):
    fmts = app.output_formats

    if not fmts:
        fmts = {x: True for x in available_formats}
    # end if

    if fmts['text']:
        process(make_texts, app, data, 'text')
    # end if

    if fmts['html']:
        process(make_htmls, app, data, 'html')
    # end if

    if fmts['mobi'] or fmts['epub']:
        epubs = process(make_epubs, app, data, 'epub')

        if fmts['mobi']:
            process(make_mobis, app, epubs, 'mobi')
        # end if
    # end if

    if fmts['pdf']:
        process(make_pdfs, app, data, 'pdf')
    # end if

    if fmts['docx']:
        process(make_docx, app, data, 'docx')
    # end if
# end def
