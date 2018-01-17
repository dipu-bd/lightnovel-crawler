from os import path, makedirs, listdir
from subprocess import call
import json
from ebooklib import epub


def convert_to_mobi(novel_id):
    input_path = path.join('_book', novel_id)
    for file_name in listdir(input_path):
        if not file_name.endswith('.epub'):
            continue
        # end if
        input_file = path.join(input_file, file_name)
        call(['kindlegen', path.abspath(input_file)])
    # end for
# end def

def convert_to_epub(novel_id):
    input_path = path.join('_data', novel_id)
    for vol in sorted(listdir(input_path)):
        data = []
        full_vol = path.join(input_path, vol)
        print('Processing:', full_vol)
        for file in sorted(listdir(full_vol)):
            full_file = path.join(full_vol, file)
            f = open(full_file, 'r')
            data.append(json.load(f))
            f.close()
        # end for
        data.sort(key=lambda x: x['chapter_no'])
        create_epub(novel_id, vol, data)
    # end for
# end def

def create_epub(novel_id, volume_no, data):
    output_path = path.join('_book', novel_id)
    vol = str(volume_no).rjust(2, '0')
    title = data[0]['novel'] + ' Volume ' + vol
    print('Creating EPUB:', title)

    book = epub.EpubBook()
    book.set_identifier(novel_id + volume_no)
    book.set_title(title)
    book.set_language('en')
    book.add_author('Sudipto Chandra')

    for item in data:
        title = (item['chapter_title'] or '....')
        xhtml_file = 'chap_' + str(item['chapter_no']).rjust(2, '0') + '.xhtml'
        xhtml = '<?xml version="1.0" encoding="UTF-8" ?>\n'\
            + '<!DOCTYPE html>'\
            + '<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">'\
            + '<head>'\
            + '<meta http-equiv="Content-Type" content="application/xhtml+xml; charset=utf-8" />'\
            + '<title>' + item['volume_title'] + '</title>'\
            + '</head>'\
            + '<body style="text-align: justify">'\
            + '<h1>' + title + '</h1>'\
            + '\n'.join([ '<p>' + x + '</p>' for x in item['body']])\
            + '</body>'\
            + '</html>'
        # add chapter
        chapter = epub.EpubHtml(title=title, file_name=xhtml_file)
        chapter.content = xhtml
        book.add_item(chapter)
    # end for

    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    if not path.exists(output_path):
        makedirs(output_path)
    # end if
    file_name = novel_id + '_v' + str(volume_no) + '.epub'
    epub.write_epub(path.join(output_path, file_name), book, {})
# def
