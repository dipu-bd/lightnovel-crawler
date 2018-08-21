#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Helper methods used in crawling"""
import os
import json

def save_chapter(content, output_path, pack_by_volume=True):
    '''save content to file'''
    dir_name = os.path.join(output_path, 'json')
    if pack_by_volume:
        vol = content['volume_no'].rjust(2, '0')
        dir_name = os.path.join(dir_name, vol)
    # end if
    try:
        os.makedirs(dir_name)
    except:
        pass
    # end if
    chap = content['chapter_no'].rjust(5, '0')
    file_name = os.path.join(dir_name, chap + '.json')
    print('Saving ', file_name)
    with open(file_name, 'w') as file:
        file.write(json.dumps(content))
    # end with
# end def
