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
    logger.debug('Binding: %s.epub', bool_title)
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
    logger.debug('Creating: %s', file_path)
    os.makedirs(epub_path, exist_ok=True)
    epub.write_epub(file_path, book, {})
    logger.warn('Created: %s.epub', bool_title)
# end def

def novel_to_mobi(input_path):
    input_path = os.path.abspath(input_path)
    epub_path = os.path.join(input_path, 'epub')
    if not os.path.exists(epub_path):
        return
    # end if
    mobi_path = os.path.join(input_path, 'mobi')
    os.makedirs(mobi_path, exist_ok=True)

    # Convert to mobi format
    no_kindlegen = False
    devnull = open(os.devnull, 'w')
    for file_name in sorted(os.listdir(epub_path)):
        if not file_name.endswith('.epub'):
            continue
        # end if

        epub_file = os.path.join(epub_path, file_name)

        fallback = False
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
                logger.error('KindleGen does not support this OS.')
                continue
            # end if
            kindlegen = os.path.join('ebook_crawler', 'ext', kindlegen)
            subprocess.call(
                [ os.path.abspath(kindlegen), epub_file ],
                stdout=devnull,
                stderr=devnull,
            )
        except Exception as ex:
            fallback = True
            logger.debug(ex)
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
            # end tr
        # end if

        mobi_filename = file_name.replace('.epub', '.mobi')
        if os.path.exists(os.path.join(epub_path, mobi_filename)):
            logger.warn('Created %s', mobi_filename)
            os.rename(
                os.path.join(epub_path, mobi_filename),
                os.path.join(mobi_path, mobi_filename),
            )
        else:
            logger.error('Failed to convert %s', epub_file)
        # end if
    # end for
    
    if no_kindlegen:
        logger.warn('')
        logger.warn('kindlegen required to generate .mobi files!')
        logger.warn('Install it from:')
        logger.warn('   https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211')
        logger.warn('')
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
