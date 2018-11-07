#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contains methods for binding novel or manga into epub and mobi"""
import re
import io
import os
import errno
import logging
import platform
from subprocess import call
from ebooklib import epub
from progress.spinner import Spinner

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
KINDLEGEN_PATH_MAC = os.path.join(DIR_NAME, '..', 'ext', 'kindlegen-mac')
KINDLEGEN_PATH_LINUX = os.path.join(DIR_NAME, '..', 'ext', 'kindlegen-linux')
KINDLEGEN_PATH_WINDOWS = os.path.join(DIR_NAME, '..', 'ext', 'kindlegen-windows')
SYSTEM_OS = platform.system()

logger = logging.getLogger('BINDER')

def bind_epub_book(app, chapters, volume=''):
    bar = Spinner('Binding: %s' % volume)
    bar.start()
    # Create book
    bool_title = (app.crawler.novel_title + ' ' + volume).strip()
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
    bar.next()
    # Make contents
    book.toc = []
    for chapter in chapters:
        xhtml_file = 'chap_%s.xhtml' % str(chapter['id']).rjust(4, '0')
        content = epub.EpubHtml(
            lang='en',
            file_name=xhtml_file,
            # uid=int(chapter['id']),
            content=chapter['body'] or '',
            title='%s — %s' % (chapter['name'], chapter['title']),
        )
        book.add_item(content)
        book.toc.append(content)
        bar.next()
    # end for
    book.spine += book.toc
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    bar.next()
    # Save epub file
    epub_path = os.path.join(app.output_path, 'epub')
    file_path = os.path.join(epub_path, bool_title + '.epub')
    logger.debug('Creating: %s', file_path)
    os.makedirs(epub_path, exist_ok=True)
    epub.write_epub(file_path, book, {})
    bar.finish()
# end def

def novel_to_mobi(input_path):
    epub_path = os.path.join(input_path, 'epub')
    if not os.path.exists(epub_path):
        print('!! Could not make mobi files. EPUB folder does not exist.')
        return
    # end if
    # Convert to mobi format
    for file_name in sorted(os.listdir(epub_path)):
        if not file_name.endswith('.epub'):
            continue
        # end if
        epub_file = os.path.join(epub_path, file_name)
        generator = lambda kindlegen: call([kindlegen, epub_file])
        try:
            if SYSTEM_OS == 'Linux':
                generator(KINDLEGEN_PATH_LINUX)
            elif SYSTEM_OS == 'Darwin':
                generator(KINDLEGEN_PATH_MAC)
            elif SYSTEM_OS == 'Windows':
                generator(KINDLEGEN_PATH_WINDOWS)
            else:
                raise Exception('KindleGen does not support this OS.')
            # end if
        except:
            try:
                generator('kindlegen')
            except (OSError, Exception) as err:
                if err[1].errno == errno.ENOENT:
                    print("Warning: kindlegen was not on your path; not generating .mobi files")
                    print("Visit https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211 to install it.")
                else:
                    print("-" * 60)
                    print("Failed to create .mobi files")
                    print()
                # end if
            # end try
        # end try
    # end for

    # Move mobi files to mobi_path
    mobi_path = os.path.join(input_path, 'mobi')
    if not os.path.exists(mobi_path):
        os.makedirs(mobi_path)
    # end if

    for file_name in sorted(os.listdir(epub_path)):
        if not file_name.endswith('.mobi'):
            continue
        # end if
        os.rename(os.path.join(epub_path, file_name), os.path.join(mobi_path, file_name))
    # end for
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
