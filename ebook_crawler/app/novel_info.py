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


def novel_info(app):
    answer = prompt([
        {
            'type': 'input',
            'name': 'novel',
            'message': 'What is the url of novel page?',
            'validate': lambda val: 'Url should be not be empty'
            if len(val) == 0 else True,
        },
    ])

    app.logger.warn('Getting novel info...')
    app.crawler.read_novel_info(answer['novel'].strip())
    app.output_path = re.sub(
        r'[\\/*?:"<>|\']', '', app.crawler.novel_title)
    app.output_path = os.path.abspath(app.output_path)

    if os.path.exists(app.output_path):
        answer = prompt([
            {
                'type': 'confirm',
                'name': 'fresh',
                'message': 'Detected existing folder. Replace it?',
                'default': False,
            },
        ])
        if answer['fresh']:
            rmtree(app.output_path)
        # end if
    # end if
    os.makedirs(app.output_path, exist_ok=True)

    app.logger.warn('Getting chapters...')
    require_saving = False
    file_name = os.path.join(app.output_path, 'meta.json')
    if os.path.exists(file_name):
        with open(file_name, 'r') as file:
            app.logger.info('Loading metadata')
            data = json.load(file)
            app.crawler.volumes = data['volumes']
            app.crawler.chapters = data['chapters']
        # end with
    else:
        require_saving = True
    # end if
    if len(app.crawler.chapters) == 0:
        require_saving = True
        app.logger.info('Fetching chapters')
        app.crawler.download_chapter_list()
        for item in app.crawler.volumes:
            title = 'Volume %d' % item['id']
            item['title'] = item['title'] or title
            if not item['title'].lower().startswith('volume'):
                item['title'] = title + ' - ' + item['title'].title()
            # end if
        # end for
        for item in app.crawler.chapters:
            title = 'Chapter #%d' % item['id']
            item['title'] = item['title'] or title
            if not item['title'].lower().startswith('chapter'):
                item['title'] = title + ' - ' + item['title'].title()
            # end if
            item['volume'] = item['volume'] or (1 + (item['id'] - 1) // 100)
            item['volume_title'] = app.crawler.volumes[item['volume'] - 1]['title']
        # end for
    # end if
    if require_saving:
        data = {
            'title': app.crawler.novel_title,
            'author': app.crawler.novel_author,
            'cover': app.crawler.novel_cover,
            'volumes': app.crawler.volumes,
            'chapters': app.crawler.chapters,
        }
        with open(file_name, 'w') as file:
            app.logger.info('Writing metadata: %s', file_name)
            json.dump(data, file, indent=2)
        # end with
    # end if
# end def
