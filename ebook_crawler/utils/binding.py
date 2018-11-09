#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contains methods for binding novel or manga into epub and mobi"""
import re
import io
import os
import errno
import logging
import platform
import subprocess
from ebooklib import epub
from progress.spinner import Spinner

KINDLEGEN_PATH_MAC = 'kindlegen-mac'
KINDLEGEN_PATH_LINUX = 'kindlegen-linux'
KINDLEGEN_PATH_WINDOWS = 'kindlegen-windows'

logger = logging.getLogger('BINDER')

def bind_epub_book(app, chapters, volume=''):
    bool_title = (app.crawler.novel_title + ' ' + volume).strip()
    logger.debug('Binding %s.epub', bool_title)
    # Create book
    book = epub.EpubBook()
    book.set_language('en')
    book.set_title(bool_title)
    book.add_author(app.crawler.novel_author)
    book.set_identifier(app.output_path + volume)
    # Create book spine
    if app.book_cover:
        book.set_cover('image.jpg', open(app.book_cover, 'rb').read())
        book.spine = ['cover', 'nav']
    else:
        book.spine = ['nav']
    # end if
    # Make contents
    book.toc = []
    for i, chapter in enumerate(chapters):
        xhtml_file = 'chap_%s.xhtml' % str(i + 1).rjust(5, '0')
        content = epub.EpubHtml(
            lang='en',
            uid=str(i + 1),
            file_name=xhtml_file,
            title=chapter['title'],
            content=chapter['body'] or '',
        )
        book.add_item(content)
        book.toc.append(content)
    # end for
    book.spine += book.toc
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    # Save epub file
    epub_path = os.path.join(app.output_path, 'epub')
    file_path = os.path.join(epub_path, bool_title + '.epub')
    logger.debug('Writing %s', file_path)
    os.makedirs(epub_path, exist_ok=True)
    epub.write_epub(file_path, book, {})
    logger.warn('Created: %s.epub', bool_title)
    return file_path
# end def

def epub_to_mobi(epub_file):
    if not os.path.exists(epub_file):
        return
    # end if

    epub_path = os.path.dirname(epub_file)
    input_path = os.path.dirname(epub_path)
    mobi_path = os.path.join(input_path, 'mobi')
    epub_file_name = os.path.basename(epub_file)
    mobi_file_name = epub_file_name.replace('.epub', '.mobi')
    mobi_file_in_epub_path = os.path.join(epub_path, mobi_file_name)
    mobi_file = os.path.join(mobi_path, mobi_file_name)
    logger.debug('Binding %s.epub', mobi_file)

    fallback = None
    devnull = open(os.devnull, 'w')
    try:
        kindlegen = None
        os_name = platform.system()
        if os_name == 'Linux':
            kindlegen = KINDLEGEN_PATH_LINUX
        elif os_name == 'Darwin':
            kindlegen = KINDLEGEN_PATH_MAC
        elif os_name == 'Windows':
            kindlegen = KINDLEGEN_PATH_WINDOWS
        else:
            fallback = 'KindleGen does not support this OS.'
        # end if

        dir_name = os.path.dirname(__file__)
        kindlegen = os.path.join(dir_name, '..', 'ext', kindlegen)
        kindlegen = os.path.abspath(kindlegen)

        subprocess.call(
            [ kindlegen, epub_file ],
            stdout=devnull,
            stderr=devnull,
        )
    except Exception as ex:
        fallback = '%s' % ex
    # end try

    if fallback:
        try:
            subprocess.call(
                [ 'kindlegen', epub_file ],
                stdout=devnull,
                stderr=devnull,
            )
        except (OSError, Exception) as err:
            no_kindlegen = no_kindlegen or (
                err[1].errno == errno.ENOENT
                if err is OSError else False
            )
        # end try
    # end if

    if os.path.exists(mobi_file_in_epub_path):
        os.makedirs(mobi_path, exist_ok=True)
        os.rename(mobi_file_in_epub_path, mobi_file)
        logger.warn('Created: %s', mobi_file_name)
    else:
        logger.error('Failed to generate mobi for %s', epub_file_name)
    # end if
# end def


#-------------------------------------------------------------------------------------------------#
def manga_to_kindle(input_path):
    '''Convert crawled data to epub'''
    manga_id = os.path.basename(input_path)
    output_path = manga_id
    name = ' '.join([x.capitalize() for x in manga_id.split('_')])
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # end if
    call(['kcc-c2e',
          '-p', 'KPW',
          # '--forcecolor',
          # '-f', 'EPUB',
          '-t', name,
          '-o', output_path,
          input_path])
# end def
