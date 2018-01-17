from os import path, makedirs, listdir
from subprocess import call
import json
import pypub


def convert_to_epub(input_path, output_path):
    for vol in sorted(listdir(input_path)):
        data = []
        full_vol = path.join(input_path, vol)
        print('Processing: ' + full_vol)
        for file in sorted(listdir(full_vol)):
            full_file = path.join(full_vol, file)
            f = open(full_file, 'r')
            data.append(json.load(f))
            f.close()
        # end for
        data.sort(key=lambda x: x['chapter_no'])
        create_epub(vol, data, output_path)
    # end for
# end def

def create_epub(volume_no, data, output_path):
    vol = str(volume_no).rjust(2, '0')
    title = epub_title + ' Volume ' + vol
    print('Creating EPUB:' + title)
    epub = pypub.Epub(title, 'Sudipto Chandra')
    for item in data:
        title = (item['chapter_title'] or '....')
        html = '<?xml version="1.0" encoding="UTF-8" ?>\n'\
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
        chapter = pypub.Chapter(content=html, title=title)
        epub.add_chapter(chapter)
    # end for
    if not path.exists(output_path):
        makedirs(output_path)
    # end if
    epub.create_epub(output_path)
# def

def convert_to_mobi(epub_path):
    for file_name in listdir(epub_path):
        if not file_name.endswith('.epub'):
            continue
        # end if
        input_file = path.join(epub_path, file_name)
        call(['kindlegen', path.abspath(input_file)])
    # end for
# end def
