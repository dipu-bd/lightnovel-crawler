#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
from PyInquirer import prompt
from ..utils.binding import bind_epub_book, epub_to_mobi

def bind_books(app):
    epub_files = []
    if app.pack_by_volume:
        for i, vol in enumerate(app.crawler.volumes):
            chapters = [
                x for x in app.chapters
                if x['volume_title'] == vol['title']
                    and len(x['body']) > 0
            ]
            if len(chapters) > 0:
                epub_files.append(bind_epub_book(
                    app,
                    chapters=chapters,
                    volume='Volume %d' % (i + 1),
                ))
            # end if
        # end for
    else:
        epub_files.append(bind_epub_book(
            app,
            chapters=app.chapters,
        ))
    # end if

    for epub in epub_files:
        epub_to_mobi(epub)
    # end for
# end def
