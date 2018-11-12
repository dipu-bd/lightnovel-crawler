#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To bind into ebooks
"""
import os
import re
from bs4 import BeautifulSoup
from PyInquirer import prompt
from ..utils.binding import bind_epub_book, epub_to_mobi

def bind_books(app):
    # DATA
    data = {}
    if app.pack_by_volume:
        for i, vol in enumerate(app.crawler.volumes):
            data['Volume %d' % vol['id']] = [
                x for x in app.chapters
                if x['volume'] == vol['id']
                    and len(x['body']) > 0
            ]
        # end for
    else:
        data[''] = app.chapters
    # end if

    # EPUB
    epub_files = []
    for vol in data:
        if len(data[vol]) > 0:
            epub_files.append(bind_epub_book(
                app,
                volume=vol,
                chapters=data[vol],
            ))
        # end if
    # end for

    # MOBI
    for epub in epub_files:
        epub_to_mobi(epub)
    # end for

    # TEXT
    for vol in data:
        for chap in data[vol]:
            dir_name = os.path.join(app.output_path, 'text', vol)
            file_name = '%s.txt' % str(chap['id']).rjust(5, '0')
            file_name = os.path.join(dir_name, file_name)
            os.makedirs(dir_name, exist_ok=True)
            with open(file_name, 'w') as file:
                body = chap['body'].replace('</p><p', '</p>\n<p')
                soup = BeautifulSoup(body, 'lxml')
                text = '\n\n'.join(soup.stripped_strings)
                text = re.sub('[\r\n]+', '\r\n\r\n', text)
                file.write(text)
            # end with
        # end for
    # end for
# end def
