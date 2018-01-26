"""
Contains methods for binding novel or manga into epub and mobi
"""
import re
import io
import os
import json
import random
from subprocess import call
from ebooklib import epub
from PIL import Image, ImageFont, ImageDraw

path = os.path

def epub_to_mobi(input_path):
    '''Converts epub file to mobi'''
    for file_name in sorted(os.listdir(input_path)):
        if not file_name.endswith('.epub'):
            continue
        input_file = os.path.join(input_path, file_name)
        kindlegen = os.path.join('lib', 'kindlegen', 'kindlegen')
        call([kindlegen, input_file])
    # end for
# end def

def novel_to_kindle(input_path):
    novel_id = os.path.basename(input_path)
    output_path = os.path.join('_book', novel_id)
    # Create epubs by volumes
    for volume_no in sorted(os.listdir(input_path)):
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
            book.add_item(chapter)
            contents.append(chapter)
            if not book_title:
                book_title = item['novel']
            # end if
        # end for
        book.spine = ['cover', 'nav'] + contents
        book.set_title(book_title + ' Volume ' + vol)
        book.toc = contents
        book.add_item(epub.EpubNav())
        book.add_item(epub.EpubNcx())
        # Generate cover
        colors = range(10, 50)
        r = random.choice(colors)
        g = random.choice(colors)
        b = random.choice(colors)
        image = Image.new('RGB', (625, 1000), (r, g, b))
        draw = ImageDraw.Draw(image)
        font_path = os.path.abspath('lib/bookman-antiqua.ttf')
        font = ImageFont.truetype(font_path, 80)
        draw.text((110, 200), 'Volume ' + vol, '#ccd', font=font)
        font = ImageFont.truetype(font_path, 100)
        print_title = re.sub(' ', '\n', book_title)
        print_title = re.sub(r'[^\x00-\x7f]|[()]', '', print_title)
        draw.text((110, 300), print_title.strip(), '#fff', font=font)
        bytes_io = io.BytesIO()
        image.save(bytes_io, format='PNG')
        book.set_cover(file_name='cover.png', content=bytes_io.getvalue())
        # Create epub
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        # end if
        file_name = novel_id + '_v' + volume_no + '.epub'
        file_path = os.path.join(output_path, file_name)
        print('Creating:', file_path)
        epub.write_epub(file_path, book, {})
    # end for
    # Convert to mobi format
    epub_to_mobi(output_path)
# end def

def manga_to_kindle(input_path):
    '''Convert crawled data to epub'''
    manga_id = os.path.basename(input_path)
    output_path = os.path.join('_book', manga_id)
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
    # epub_to_mobi(output_path)
# end def
