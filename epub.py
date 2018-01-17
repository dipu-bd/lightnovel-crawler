#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Creates an epub from crawled data

Requirements:
Pypub: pip install pypub
"""
from os import path, listdir, makedirs
import json
import pypub

# Settings
input_path = '_data/atte'
output_path = '_epub/atte'
file_name_prefix = 'ATTE'
epub_title = 'A Thought Through Eternity'


def start():
    for vol in sorted(listdir(input_path)):
        data = []
        full_vol = path.join(input_path, vol)
        print 'Processing:', full_vol
        for file in sorted(listdir(full_vol)):
            full_file = path.join(full_vol, file)
            f = open(full_file, 'r')
            data.append(json.load(f))
            f.close()
        # end for
        create_epub(vol, data)
    # end for
# end def

def create_dir(file):
    if not path.exists(path.dirname(file)):
        makedirs(path.dirname(file))
    # end if
# end def

def create_epub(volume_no, data):
    epub = pypub.Epub(epub_title)
    for item in data:
        body = '\n'.join([ '<p>' + x + '</p>' for x in item['body']])
        body = '<div style="text-align: justify">' + body + '</div>'
        # head = '<head><title>' + item['chapter_title'] + '</title></head>'
        # html = '<html>' + head + body + '</html>'
        epub.add_chapter(pypub.Chapter(content=body, title=item['chapter_title']))
    # end for
    file_name = file_name_prefix + '_v' + str(volume_no) + '.epub'
    create_dir(file_name)
    epub.create_epub(file_name)
# def

if __name__ == '__main__':
    start()
# end if
