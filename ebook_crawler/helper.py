#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper methods used in crawling"""
import json
from os import path, makedirs

def save_chapter(content, output_path):
    '''save content to file'''
    print(content['volume_no'])
    if content['volume_no'] == '0':
        vol = ''
    else :
        vol = content['volume_no'].rjust(2, '0')
    chap = content['chapter_no'].rjust(5, '0')
    dir_name = path.join(output_path, vol)
    try:
        makedirs(dir_name)
    except:
        pass
    # end if
    file_name = path.join(dir_name, chap + '.json')
    print('Saving ', file_name)
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def
