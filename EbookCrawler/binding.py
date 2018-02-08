#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Contains methods for binding novel or manga into epub and mobi"""
import re
import io
import os
import json
import random
import textwrap
from subprocess import call
from ebooklib import epub
from PIL import Image, ImageFont, ImageDraw

KINDLEGEN_PATH = os.path.join('lib', 'kindlegen', 'kindlegen')
BOOK_PATH = '_book'


def novel_to_kindle(input_path):
    ''''Convert novel to epub'''
    novel_id = os.path.basename(input_path)
    output_path = os.path.join(BOOK_PATH, novel_id)
    # Create epubs by volumes
    for volume_no in sorted(os.listdir(input_path)):
        try:
            # create book
            book = epub.EpubBook()
            book.set_identifier(novel_id + volume_no)
            book.set_language('en')
            book.add_author('Sudipto Chandra')
            # get chapters
            contents = []
            book_title = None
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
                # chapter.content += '<style>%s</style>' % (open('style.css').read())
                book.add_item(chapter)
                contents.append(chapter)
                if not book_title:
                    book_title = item['novel']
                # end if
            # end for
            book.spine = ['nav'] + contents
            book.set_title(book_title + ' Volume ' + vol)
            book.toc = contents
            book.add_item(epub.EpubNav())
            book.add_item(epub.EpubNcx())
            # # Generate cover
            # print_title = re.sub(r'[^\x00-\x7f]|[()]', '', book_title)
            # if len(print_title) > 35:
            #     print_title = print_title[:35] + '...'
            # print_title = textwrap.fill(print_title, 8)
            # print_title = '\n'.join(print_title.splitlines()[:6])
            # color = random.choice(range(200, 230))
            # image = Image.new('RGB', (660, 1000), (color, color, color))
            # draw = ImageDraw.Draw(image)
            # font_path = os.path.abspath('lib/bookman-antiqua.ttf')
            # font = ImageFont.truetype(font_path, 80)
            # draw.text((120, 200), 'Volume ' + vol, '#444', font=font)
            # font = ImageFont.truetype(font_path, 100)
            # draw.text((120, 300), print_title.strip(), '#000', font=font)
            # bytes_io = io.BytesIO()
            # image.save(bytes_io, format='PNG')
            # book.set_cover(file_name='cover.png', content=bytes_io.getvalue())
            # Create epub
            if not os.path.exists(output_path):
                os.makedirs(output_path)
            # end if
            file_name = novel_id + '_v' + volume_no + '.epub'
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
