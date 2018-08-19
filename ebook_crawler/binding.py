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

def novel_to_kindle(input_path, pack_by_volume):
    ''''Convert novel to epub'''
    if not os.path.exists(input_path):
        return print(input_path, 'does not exists')
    # end if
    novel_id = os.path.basename(input_path)
    # Create epubs by volumes
    output_path = None
    if not pack_by_volume:
        try:
            output_path = bind_book(input_path, novel_id)
        except:
            print('!! Failed to bind:', input_path)
        # end try
    else :
        for volume_no in sorted(os.listdir(input_path)):
            try:
                output_path = bind_book(input_path, novel_id, volume_no)
            except:
                print('!! Failed to bind:', input_path, volume_no)
            # end try
        # end for
    #end if
    if output_path:
        convert_to_mobi(output_path)
    # end if
# end def

def bind_book(input_path, novel_id, volume_no = ''):
    # create book
    book = epub.EpubBook()
    book.set_identifier(novel_id + volume_no)
    book.set_language('en')
    vol = ''
    if volume_no and volume_no != '':
        vol = ' Volume ' + volume_no.rjust(2, '0')
    # end if
    # get chapters
    contents = []
    book_title = None
    book_author = None
    book_cover = None
    full_vol = os.path.join(input_path, volume_no)
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
        if not book_title: book_title = item['novel']
        if not book_cover: book_cover = item['cover']
        if not book_author and 'author' in item: book_author = item['author']
    # end for
    book_title = book_title or 'N/A'
    book_cover = book_cover or 'N/A'
    book_author = book_author or 'N/A'
    book.spine = ['cover','nav'] + contents
    book.add_author(book_author)
    if book_cover and book_cover != 'N/A':
        try:
            filename=book_cover.split('/')[-1]
            opener = urllib.request.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')]
            urllib.request.install_opener(opener)
            urllib.request.urlretrieve(book_cover, filename)
            book.set_cover("image.jpg", open(filename, 'rb').read())
        except:
            print('Failed to add cover:', book_cover)
            pass
        # end try
    #endif
    book.set_title(book_title + vol)
    book.toc = contents
    book.add_item(epub.EpubNav())
    book.add_item(epub.EpubNcx())
    # Create epub
    book_title = re.sub('[\\\\/*?:"<>|]' or r'[\\/*?:"<>|]',"", book_title)
    output_path = book_title
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # end if
    file_name = book_title + '_v' + volume_no + '.epub'
    file_path = os.path.join(output_path, file_name)
    print('Creating:', file_path)
    epub.write_epub(file_path, book, {})
    return output_path
# end def

def convert_to_mobi(output_path):
    # Convert to mobi format
    for file_name in sorted(os.listdir(output_path)):
        if not file_name.endswith('.epub'):
            continue
        # end if
        epub_file = os.path.join(output_path, file_name)
        try:
            kindlegen = None
            if SYSTEM_OS == 'Linux':
                kindlegen = KINDLEGEN_PATH_LINUX
            elif SYSTEM_OS == 'Darwin':
                kindlegen = KINDLEGEN_PATH_MAC
            elif SYSTEM_OS == 'Windows':
                kindlegen = KINDLEGEN_PATH_WINDOWS
            else:
                raise Exception('KindleGen does not support this OS.')
            # end if
            call([kindlegen, '-c2', epub_file])
        except:
            try:
                call(['kindlegen', '-c2', epub_file])
            except (OSError, Exception) as err:
                if err[1].errno == errno.ENOENT:
                    print("Warning: kindlegen was not on your path; not generating .mobi version")
                    print("Visit https://www.amazon.com/gp/feature.html?ie=UTF8&docId=1000765211 to install it.")
                else:
                    print("-" * 60)
                    print("Failed to create .mobi files")
                    print()
                # end if
            # end try
        # end try
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
