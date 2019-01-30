#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
import logging
import shutil
import os

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
    except Exception as ex:
        logger.debug(ex)
        logger.warn('Failed to generate *.%s files' % fmt)
        return None
    # end try
# end def


def bind_books(app, data):
    text = app.output_formats
    fmts = {}
    if not text or text=='all':
        fmts = {x: True for x in available_formats}
    else:
        for x in available_formats:
            if x == text:
                fmts[x]=True
            else:
                fmts[x]=False
            # end if
        #end for    
    #end if

    if fmts['text']:
        process(make_texts, app, data, 'text')
        if text!='all':
            logger.info('Compressing text output...')
            text_path = os.path.join(app.output_path, 'text')
            text_archived_output = shutil.make_archive(text_path, 'zip', app.output_path)
            logger.warn('Compressed to %s' % text_archived_output)
            output=[]
            output.append(text_archived_output)
        #end if
    # end if

    if fmts['html']:
        output = process(make_htmls, app, data, 'html')
        if text!='all':
            logger.info('Compressing html output...')
            html_path = os.path.join(app.output_path, 'html')
            html_archived_output = shutil.make_archive(html_path, 'zip', app.output_path)
            logger.warn('Compressed to %s' % html_archived_output)
            output=[]
            output.append(html_archived_output)
        #end if
    # end if

    if fmts['mobi'] or fmts['epub']:
        epubs = process(make_epubs, app, data, 'epub')
        output = epubs
        if fmts['mobi']:
            output = process(make_mobis, app, epubs, 'mobi')
        # end if
    # end if

    if fmts['pdf']:
        output = process(make_pdfs, app, data, 'pdf')
    # end if

    if fmts['docx']:
        output = process(make_docx, app, data, 'docx')
    # end if
    print(output)
    return output
# end def
