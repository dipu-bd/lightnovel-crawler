#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
To get the novel info
"""
import json
import os
import re
from shutil import rmtree
from PyInquirer import prompt

def get_novel_url():
    answer = prompt([
        {
            'type': 'input',
            'name': 'novel',
            'message': 'What is the url of novel page?',
            'validate': lambda val: 'Url should be not be empty'
            if len(val) == 0 else True,
        },
    ])
    return answer['novel'].strip()
# end def

def check_output_path(output_path):
    if os.path.exists(output_path):
        answer = prompt([
            {
                'type': 'confirm',
                'name': 'fresh',
                'message': 'Detected existing folder. Replace it?',
                'default': False,
            },
        ])
        if answer['fresh']:
            rmtree(output_path)
        # end if
    # end if
    os.makedirs(output_path, exist_ok=True)
# end def

def retrieve_chapter_list(crawler, output_path):
    file_name = os.path.join(output_path, 'meta.json')
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            data = json.load(file)
            crawler.volumes = data['volumes']
            crawler.chapters = data['chapters']
        # end with
    # end if
    
    if len(crawler.chapters) == 0:
        crawler.download_chapter_list()
    # end if
# end def

def format_volume_list(crawler):
    for vol in crawler.volumes:
        vol['chapter_count'] = 0
        title = 'Volume %d' % vol['id']
        vol['title'] = vol['title'] or title
        if not re.search(r'vol(ume)? .?\d+', vol['title'], re.IGNORECASE):
            vol['title'] = title + ' - ' + vol['title'].title()
        # end if
    # end for
# end def

def format_chapter_list(crawler):
    for item in crawler.chapters:
        title = 'Chapter #%d' % item['id']
        item['title'] = item['title'] or title
        if not re.search(r'ch(apter)? .?\d+', item['title'], re.IGNORECASE):
            item['title'] = title + ' - ' + item['title'].title()
        # end if

        item['volume'] = item['volume'] or (1 + (item['id'] - 1) // 100)
        item['volume_title'] = 'Volume %d' % item['volume']
        for vol in crawler.volumes:
            if vol['id'] == item['volume']:
                item['volume_title'] = vol['title']
                vol['chapter_count'] += 1
                break
            # end if
        # end for
    # end for
# end def

def save_metadata(crawler, output_path):
    file_name = os.path.join(output_path, 'meta.json')
    data = {
        'title': crawler.novel_title,
        'author': crawler.novel_author,
        'cover': crawler.novel_cover,
        'volumes': crawler.volumes,
        'chapters': crawler.chapters,
    }
    with open(file_name, 'w') as file:
        json.dump(data, file, indent=2)
    # end with
# end def

def novel_info(app):
    app.logger.info('Retrieving novel info...')
    app.crawler.read_novel_info(get_novel_url())

    app.logger.info('Checking output path...')
    app.output_path = os.path.abspath(
        re.sub(r'[\\/*?:"<>|\']', '', app.crawler.novel_title))
    check_output_path(app.output_path)

    app.logger.info('Getting chapters...')
    retrieve_chapter_list(app.crawler, app.output_path)

    format_volume_list(app.crawler)
    format_chapter_list(app.crawler)

    save_metadata(app.crawler, app.output_path)
# end def
