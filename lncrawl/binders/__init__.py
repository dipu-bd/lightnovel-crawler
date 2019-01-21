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


def bind_books(app, data):
    fmts = app.output_formats
    if not fmts:
        fmts = { x: True for x in available_formats }
    # end if

    if fmts['text']:
        make_texts(app, data)
    # end if

    if fmts['html']:
        make_htmls(app, data)
    # end if

    if fmts['mobi'] or fmts['epub']:
        epubs = make_epubs(app, data)

        if fmts['mobi']:
            make_mobis(app, epubs)
        # end if
    # end if

    if fmts['pdf']:
        make_pdfs(app, data)
    # end if

    if fmts['docx']:
        make_docx(app, data)
    # end if
# end def
