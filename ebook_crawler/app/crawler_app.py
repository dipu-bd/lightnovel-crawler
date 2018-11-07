#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""

import concurrent.futures
import json
import logging
import os
import re
import shutil

from bs4 import BeautifulSoup
from ebooklib import epub
from PIL import Image, ImageDraw, ImageFont
from progress.bar import IncrementalBar
from progress.spinner import Spinner
from PyInquirer import prompt

from .binding import bind_epub_book, novel_to_mobi
from .helper import clean_filename, retrieve_image
from .validators import validateNumber

logger = logging.getLogger('CRAWLER_APP')


class CrawlerApp:
    crawler = None

    def start(self):
        if not self.crawler:
            logger.error('Crawler is not defined')
            return
        # end if
        try:
            if self.crawler.supports_login:
                self.login()
            # end if
            self.novel_info()

            self.chapter_range()
            self.additional_configs()
            self.download_chapters()

            self.bind_books()
        except Exception as ex:
            logger.error(ex)
            raise ex
        # end try
    # end def

    def login(self):
        answer = prompt([
            {
                'type': 'confirm',
                'name': 'login',
                'message': 'Do you want to log in?',
                'default': False
            },
        ])
        if answer['login']:
            answer = prompt([
                {
                    'type': 'input',
                    'name': 'email',
                    'message': 'Email:',
                    'validate': lambda val: 'Email address should be not be empty'
                    if len(val) == 0 else True,
                },
                {
                    'type': 'password',
                    'name': 'password',
                    'message': 'Password:',
                    'validate': lambda val: 'Password should be not be empty'
                    if len(val) == 0 else True,
                },
            ])
            self.crawler.login(answer['email'], answer['password'])
        # end if
    # end def

    def novel_info(self):
        answer = prompt([
            {
                'type': 'input',
                'name': 'novel',
                'message': 'What is the url of novel page?',
                'validate': lambda val: 'Url should be not be empty'
                if len(val) == 0 else True,
            },
        ])
        self.crawler.read_novel_info(answer['novel'].strip())
        self.output_path = clean_filename(self.crawler.novel_title)
    # end def

    def chapter_range(self):
        choices = [
            'Last 10 chapters',
            'First 10 chapters',
            'Everything!',
            'Custom range using URL',
            'Custom range using index',
            'Select specific volumes',
            'Select specific chapters (warning: a large list will be displayed)'
        ]
        answer = prompt([
            {
                'type': 'list',
                'name': 'choice',
                'message': 'Which chapters to download?',
                'choices': choices
            },
        ])
        if choices[0] == answer['choice']:
            pass
        elif choices[1] == answer['choice']:
            self.chapters = self.crawler.chapters[-10:]
        elif choices[2] == answer['choice']:
            self.chapters = self.crawler.chapters[:10]
        elif choices[3] == answer['choice']:
            self.range_using_urls()
        elif choices[4] == answer['choice']:
            self.range_using_index()
        elif choices[5] == answer['choice']:
            self.range_from_volumes()
        elif choices[6] == answer['choice']:
            self.range_from_chapters()
        # end if
        logger.debug('Selected chapters to download')
        logger.debug(self.crawler.chapters)
    # end def

    def range_using_urls(self):
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start url:',
                'validate': lambda val: 'Url should be not be empty'
                if len(val) == 0 else True,
            },
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final url:',
                'validate': lambda val: 'Url should be not be empty'
                if len(val) == 0 else True,
            },
        ])
        start = 0
        stop = len(self.crawler.chapters) - 1
        start_url = answer['start'].strip(' /')
        stop_url = answer['stop'].strip(' /')
        for i, chapter in enumerate(self.crawler.chapters):
            if chapter['url'] == start_url:
                start = i
            elif chapter['url'] == stop_url:
                stop = i
            # end if
        # end for
        if stop < start:
            start, stop = stop, start
        # end if
        self.chapters = self.crawler.chapters[start:(stop + 1)]
    # end def

    def range_using_index(self):
        length = len(self.crawler.chapters)
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start index (1 to %d):' % length,
                'validate': lambda val: validateNumber(val, 1, length),
                'filter': lambda val: int(val) - 1,
            },
        ])
        start = answer['start']
        answer = prompt([
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final index (%d to %d):' % (start, length),
                'validate': lambda val: validateNumber(val, start, length),
                'filter': lambda val: int(val) - 1,
            },
        ])
        stop = answer['stop']
        self.chapters = self.crawler.chapters[start:(stop + 1)]
    # end def

    def range_from_volumes(self):
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'volumes',
                'message': 'Choose volumes to download',
                'choices': [
                    {'name': vol['title']}
                    for vol in self.crawler.volumes
                ],
                'validate': lambda ans: 'You must choose at least one volume.'
                if len(ans) == 0 else True
            }
        ])
        selected = answer['volumes']
        chapters = [
            chap for chap in self.crawler.chapters
            if selected.count(chap['volume']) > 0
        ]
        self.crawler.start_index = 0
        self.crawler.stop_index = len(chapters)
        self.chapters = chapters
    # end def

    def range_from_chapters(self):
        answer = prompt([
            {
                'type': 'checkbox',
                'name': 'chapters',
                'message': 'Choose chapters to download',
                'choices': [
                    {'name': '%d - %s' % (chap['id'], chap['title'])}
                    for chap in self.crawler.chapters
                ],
                'validate': lambda ans: 'You must choose at least one chapter.'
                if len(ans) == 0 else True
            }
        ])
        selected = [
            int(val.split(' ')[0]) - 1
            for val in answer['chapters']
        ]
        chapters = [
            chap for chap in self.crawler.chapters
            if selected.count(chap['id']) > 0
        ]
        self.crawler.start_index = 0
        self.crawler.stop_index = len(chapters)
        self.chapters = chapters
    # end def

    def additional_configs(self):
        answer = prompt([
            # {
            #     'type': 'checkbox',
            #     'name': 'formats',
            #     'choices': [
            #        { 'name': 'JSON', 'checked': True },
            #        { 'name': 'EPUB', 'checked': True },
            #        { 'name': 'MOBI' },
            #         # Plan for future
            #         #{ 'name': 'HTML' },
            #         #{ 'name': 'TEXT' },
            #         #{ 'name': 'PDF' },
            #         #{ 'name': 'RTF' },
            #         #{ 'name': 'DOCX' },
            #     ],
            #     'message': 'Which output formats to generate',
            #     'validate': lambda val: 'At least one output format required'
            #     if len(val) == 0 else True,
            # },
            {
                'type': 'confirm',
                'name': 'fresh',
                'message': 'Replace old downloads?',
                'default': False,
            },
            {
                'type': 'confirm',
                'name': 'volume',
                'message': 'Generate separate files for each volumes?',
                'default': True,
            },
        ])
        # self.formats = answer['formats']
        self.remove_old = answer['fresh']
        self.pack_by_volume = answer['volume']
    # end def

    def download_chapters(self):
        if self.remove_old and os.path.exists(self.output_path):
            shutil.rmtree(self.output_path)
        # end if
        os.makedirs(self.output_path, exist_ok=True)

        if self.crawler.novel_cover is not None:
            try:
                bar = Spinner('Downloading cover image')
                bar.start()
                filename = self.crawler.novel_cover.split('/')[-1]
                filename = os.path.join(self.output_path, filename)
                retrieve_image(self.crawler.novel_cover, filename)
                self.book_cover = filename
                bar.finish()
                logger.info('Saved cover: %s', filename)
            except Exception as ex:
                bar.finish()
                self.book_cover = None
                logger.warning('Failed to add cover: %s', ex)
            # end try
        # end if

        self.save_metadata()

        bar = IncrementalBar('Downloading chapters', max=len(self.chapters))
        bar.start()
        for chapter in self.chapters:
            dir_name = os.path.join(self.output_path, 'json')
            if self.pack_by_volume:
                dir_name = os.path.join(dir_name, chapter['volume'])
            # end if
            chapter_name = str(chapter['id']).rjust(5, '0')
            file_name = os.path.join(dir_name, chapter_name + '.json')

            if os.path.exists(file_name):
                logger.info('Restoring from %s', file_name)
                with open(file_name, 'r') as file:
                    old_chapter = json.load(file)
                    chapter['body'] = old_chapter['body']
                # end with
            else:
                logger.info('Downloading to %s', file_name)
                chapter['body'] = self.crawler.download_chapter(chapter)
                os.makedirs(dir_name, exist_ok=True)
                with open(file_name, 'w') as file:
                    file.write(json.dumps(chapter))
                # end with
            # end if
            bar.next()
        # end for
        bar.finish()
    # end def

    def save_metadata(self):
        data = {
            'title': self.crawler.novel_title,
            'author': self.crawler.novel_author,
            'cover': self.crawler.novel_cover,
            'volumes': self.crawler.volumes,
            'chapters': self.crawler.chapters,
        }
        file_name = os.path.join(self.output_path, 'meta.json')
        with open(file_name, 'w') as file:
            logger.info('Writing metadata: %s', file_name)
            json.dump(data, file, indent=2)
        # end with
    # end def

    def bind_books(self):
        if self.pack_by_volume:
            bind_epub_book(
                self,
                chapters=self.chapters,
            )
        else:
            for vol in self.crawler.volumes:
                chapters = [
                    x for x in self.chapters
                    if x['volume'] == vol['title']
                ]
                bind_epub_book(
                    self,
                    chapters=chapters,
                    volume=vol['title'],
                )
            # end for
        # end if
        novel_to_mobi(self.output_path)
    # end def
# end class
