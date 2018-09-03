#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contains methods for binding novel or manga into epub and mobi"""
import re
import io
import os
import json
import errno
import random
import textwrap
import platform
import urllib
from subprocess import call
from ebooklib import epub
from PIL import Image, ImageFont, ImageDraw
from bs4 import BeautifulSoup

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
KINDLEGEN_PATH_MAC = os.path.join(DIR_NAME, 'ext', 'kindlegen-mac')
KINDLEGEN_PATH_LINUX = os.path.join(DIR_NAME, 'ext', 'kindlegen-linux')
KINDLEGEN_PATH_WINDOWS = os.path.join(DIR_NAME, 'ext', 'kindlegen-windows')
SYSTEM_OS = platform.system()

def novel_to_epub(input_path, pack_by_volume):
    ''''Convert novel to epub'''
    if not os.path.exists(input_path):
        return print(input_path, 'does not exists')
    # end if
    # Create epubs by volumes
    if not pack_by_volume:
        _bind_book(input_path)
    else :
        json_path = os.path.join(input_path, 'json')
        for volume_no in sorted(os.listdir(json_path)):
            _bind_book(input_path, volume_no)
        # end for
    #end if
# end def

def _bind_book(input_path, volume_no = ''):
    # create book
    book = epub.EpubBook()
    book.set_language('en')
    book.set_identifier(input_path + volume_no)

    # get chapters
    contents = []
    book_title = 'N/A'
    book_author = 'N/A'
    book_cover = 'N/A'
    full_vol = os.path.join(input_path, 'json', volume_no)
    print('Processing:', full_vol)
    for file_name in sorted(os.listdir(full_vol)):
        # read data
        full_file = os.path.join(full_vol, file_name)
        item = json.load(open(full_file, 'r'))
        # add chapter
        xhtml_file = 'chap_%s.xhtml' % item['chapter_no'].rjust(4, '0')
        chapter = epub.EpubHtml(
            lang='en',
            file_name=xhtml_file,
            uid=item['chapter_no'],
            content=item['body'] or '',
            title=item['chapter_title'])
        book.add_item(chapter)
        contents.append(chapter)
        book_title = item['novel'] if 'novel' in item else book_title
        book_cover = item['cover'] if 'cover' in item else book_cover
        book_author = item['author'] if 'author' in item else book_author
    # end for

    book.add_author(book_author)
    book.spine = ['nav'] + contents
    if book_cover != 'N/A':
        try:
            filename = os.path.join(input_path, book_cover.split('/')[-1])
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(book_cover, filename)
            book.set_cover('image.jpg', open(filename, 'rb').read())
            book.spine = ['cover'] + book.spine
        except:
            print('Failed to add cover:', book_cover)
            pass
        # end try
    # end if

    if volume_no and volume_no != '':
        vol = ' Volume ' + volume_no.rjust(2, '0')
        book.set_title(book_title + vol)
    else:
        book.set_title(book_title)
    # end if
    book.toc = contents
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())

    # Save epub file
    epub_path = os.path.join(input_path, 'epub')
    if not os.path.exists(epub_path):
        os.makedirs(epub_path)
    # end if
    file_name = book_title + '_v' + volume_no + '.epub'
    file_path = os.path.join(epub_path, file_name)
    print('Creating:', file_path)
    epub.write_epub(file_path, book, {})
    return epub_path
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
