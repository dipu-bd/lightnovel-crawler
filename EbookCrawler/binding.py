#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Contains methods for binding novel or manga into epub and mobi"""
import re
import io
import os
import json
import random
import textwrap
from subprocess import call
from PIL import Image, ImageFont, ImageDraw

DIR_NAME = os.path.dirname(os.path.abspath(__file__))
KINDLEGEN_PATH = os.path.join(DIR_NAME, 'lib', 'kindlegen')
BOOK_PATH = '_book'

try:
    from ebooklib import epub
except:
    print('Package Not Found: ebooklib. You can install it using:')
    print('    python3 -m pip install --user --upgrade ebooklib')
    print()
# end try


def novel_to_kindle(input_path):
    ''''Convert novel to epub'''
    if not os.path.exists(input_path):
        return print(input_path, 'does not exists')
    # end if
    novel_id = os.path.basename(input_path)
    # Create epubs by volumes
    for volume_no in sorted(os.listdir(input_path)):
        try:
            # create book
            book = epub.EpubBook()
            book.set_identifier(novel_id + volume_no)
            book.set_language('en')
            # get chapters
            contents = []
            book_title = None
            book_author = None
            vol = volume_no.rjust(2, '0')
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
                if not book_author and 'author' in item: book_author = item['author']
            # end for
            book_title = book_title or 'Unknown'
            book_author = book_author or 'Unknown'
            book.spine = ['nav'] + contents
            book.add_author(book_author)
            book.set_title(book_title + ' Volume ' + vol)
            book.toc = contents
            book.add_item(epub.EpubNav())
            book.add_item(epub.EpubNcx())
            # Create epub
            output_path = os.path.join(BOOK_PATH, book_title)
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            # end if
            file_name = book_title + '_v' + volume_no + '.epub'
            file_path = os.path.join(output_path, file_name)
            print('Creating:', file_path)
            epub.write_epub(file_path, book, {})
        except:
            pass
        # end try
    # end for

    # Convert to mobi format
    for file_name in sorted(os.listdir(output_path)):
        if not file_name.endswith('.epub'):
            continue
        epub_file = os.path.join(output_path, file_name)
        call([KINDLEGEN_PATH, epub_file])
    # end for
# end def


def manga_to_kindle(input_path):
    '''Convert crawled data to epub'''
    manga_id = os.path.basename(input_path)
    output_path = os.path.join(BOOK_PATH, manga_id)
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
