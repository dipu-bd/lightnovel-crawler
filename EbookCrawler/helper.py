#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Helper methods used in crawling"""
import json
from os import path, makedirs
from splinter import Browser

CHROME_DRIVER = path.join('lib', 'chromedriver')


def get_browser():
    '''open a headless chrome browser in incognito mode'''
    return Browser('chrome',
                   headless=True,
                   incognito=True,
                   executable_path=CHROME_DRIVER)
# end def


def save_chapter(content, output_path):
    '''save content to file'''
    vol = content['volume_no'].rjust(2, '0')
    chap = content['chapter_no'].rjust(5, '0')
    file_name = path.join(output_path, vol, chap + '.json')
    print('Saving ', file_name)
    if not path.exists(path.dirname(file_name)):
        makedirs(path.dirname(file_name))
    # end if
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def
