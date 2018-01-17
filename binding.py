import os
from os import path
from subprocess import call
import json
from ebooklib import epub


def convert_to_mobi(novel_id):
    '''Converts epub file to mobi'''
    input_path = path.join('_book', novel_id)
    for file_name in sorted(os.listdir(input_path)):
        if not file_name.endswith('.epub'):
            continue
        # end if
        input_file = path.join(input_path, file_name)
        kindlegen = path.join('lib', 'kindlegen', 'kindlegen')
        call([kindlegen, input_file])
    # end for
# end def

def convert_to_epub(novel_id):
    '''Convert crawled data to epub'''
    input_path = path.join('_data', novel_id)
    for vol in sorted(os.listdir(input_path)):
        content = []
        full_vol = path.join(input_path, vol)
        print('Processing:', full_vol)
        for file_name in sorted(os.listdir(full_vol)):
            full_file = path.join(full_vol, file_name)
            with open(full_file, 'r') as file:
                content.append(json.load(file))
            # end with
        # end for
        content.sort(key=lambda x: int(x['chapter_no']))
        create_epub(novel_id, vol, content)
    # end for
# end def

def create_epub(novel_id, volume_no, data):
    '''Creates and store epub from list of chapters'''
    output_path = path.join('_book', novel_id)
    vol = volume_no.rjust(2, '0')
    title = data[0]['novel'] + ' Volume ' + vol
    print('Creating EPUB:', title)

    book = epub.EpubBook()
    book.set_identifier(novel_id + volume_no)
    book.set_title(title)
    book.set_language('en')
    book.add_author('Sudipto Chandra')

    contents = []
    for item in data:
        title = (item['chapter_title'] or '....')
        body = '<h1>' + title + '</h1>'
        body += '\n'.join(['<p>' + x + '</p>' for x in item['body']])
        file_name = 'chap_' + item['chapter_no'].rjust(2, '0') + '.xhtml'
        # add chapter
        chapter = epub.EpubHtml(
            uid=item['chapter_no'],
            title=title,
            file_name=file_name,
            content=body,
            lang='en')
        book.add_item(chapter)
        contents.append(chapter)
    # end for

    book.toc = contents
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = ['nav'] + contents

    if not path.exists(output_path):
        os.makedirs(output_path)
    # end if
    file_name = novel_id + '_v' + volume_no + '.epub'
    epub.write_epub(path.join(output_path, file_name), book, {})
# def
