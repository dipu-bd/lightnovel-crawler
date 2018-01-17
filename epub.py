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
        data.sort(key=lambda x: x['chapter_no'])
        create_epub(vol, data)
    # end for
# end def

def create_epub(volume_no, data):
    vol = str(volume_no).rjust(2, '0')
    title = epub_title + ' Volume ' + vol
    print 'Creating EPUB:', title
    epub = pypub.Epub(title, 'Sudipto Chandra')
    for item in data:
        chap = str(item['chapter_no'])
        title = 'Chapter ' + chap + ': ' + (item['chapter_title'] or '....')
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
    epub.create_epub(path.abspath(output_path))
# def

if __name__ == '__main__':
    start()
# end if
