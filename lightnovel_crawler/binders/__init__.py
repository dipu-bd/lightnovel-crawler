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

logger = logging.Logger('BINDERS')


def make_data(app):
    data = {}
    if app.pack_by_volume:
        for vol in app.crawler.volumes:
            data['Volume %d' % vol['id']] = [
                x for x in app.chapters
                if x['volume'] == vol['id']
                and len(x['body']) > 0
            ]
        # end for
    else:
        data[''] = app.chapters
    # end if
    return data
# end def


def bind_books(app):
    data = make_data(app)
    make_texts(app, data)
    make_htmls(app, data)
    epubs = make_epubs(app, data)
    make_mobis(app, epubs)
# end def
