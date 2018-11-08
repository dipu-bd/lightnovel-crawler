#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive application to take user inputs
"""

import json
import logging
import os
import re
import shutil
from concurrent import futures

from progress.bar import IncrementalBar
from progress.spinner import Spinner
from PyInquirer import prompt

from .binding import bind_epub_book, novel_to_mobi
from .helper import retrieve_image
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

            if self.crawler.supports_login:
                self.crawler.logout()
            # end if

            self.bind_books()
        except Exception as ex:
            logger.error(ex)
            raise ex  # TODO: suppress error
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

        logger.warn('Getting novel info...')
        self.crawler.read_novel_info(answer['novel'].strip())
        self.output_path = re.sub(
            r'[\\/*?:"<>|\']', '', self.crawler.novel_title)
        self.output_path = os.path.abspath(self.output_path)

        if os.path.exists(self.output_path):
            answer = prompt([
                {
                    'type': 'confirm',
                    'name': 'fresh',
                    'message': 'Detected existing folder. Replace it?',
                    'default': False,
                },
            ])
            if answer['fresh']:
                shutil.rmtree(self.output_path)
            # end if
        # end if
        os.makedirs(self.output_path, exist_ok=True)

        logger.warn('Getting chapters...')
        require_saving = False
        file_name = os.path.join(self.output_path, 'meta.json')
        if os.path.exists(file_name):
            with open(file_name, 'r') as file:
                logger.info('Loading metadata')
                data = json.load(file)
                self.crawler.volumes = data['volumes']
                self.crawler.chapters = data['chapters']
            # end with
        else:
            require_saving = True
        # end if
        if len(self.crawler.chapters) == 0:
            require_saving = True
            logger.info('Fetching chapters')
            self.crawler.download_chapter_list()
        # end if
        if require_saving:
            data = {
                'title': self.crawler.novel_title,
                'author': self.crawler.novel_author,
                'cover': self.crawler.novel_cover,
                'volumes': self.crawler.volumes,
                'chapters': self.crawler.chapters,
            }
            with open(file_name, 'w') as file:
                logger.info('Writing metadata: %s', file_name)
                json.dump(data, file, indent=2)
            # end with
        # end if
    # end def

    def chapter_range(self):
        length = len(self.crawler.chapters)
        choices = {
            'Everything! (%d chapters)' % length: (lambda list: list),
            'Custom range using URL': (lambda x: self.range_using_urls()),
            'Custom range using index': (lambda x: self.range_using_index()),
            'Select specific volumes': (lambda x: self.range_from_volumes()),
            'Select specific chapters %s' % ('(warn: very big list)' if length > 50 else ''): (lambda x: self.range_from_chapters()),
        }
        if length >= 20:
            choices.update({
                'First 10 chapters': (lambda list: list[:10]),
                'Last 10 chapters': (lambda list: list[-10:]),
            })
        # end if

        answer = prompt([
            {
                'type': 'list',
                'name': 'choice',
                'message': 'Which chapters to download?',
                'choices': choices.keys()
            },
        ])
        self.chapters = choices[answer['choice']](self.crawler.chapters) or []
        logger.debug('Selected chapters to download:')
        logger.debug(self.chapters)
        logger.info('%d chapters to be downloaded', len(self.chapters))

        if not len(self.chapters):
            raise Exception('No chapters selected')
        # end if
    # end def

    def range_using_urls(self):
        def validator(val): return 'No such chapter found given the url' \
            if self.crawler.get_chapter_index_of(val) < 0 else True,

        def filtered(val): return self.crawler.get_chapter_index_of(val)
        answer = prompt([
            {
                'type': 'input',
                'name': 'start',
                'message': 'Enter start url:',
                'validate': validator,
            },
            {
                'type': 'input',
                'name': 'stop',
                'message': 'Enter final url:',
                'validate': validator,
            },
        ])
        start = filtered(answer['start'])
        stop = filtered(sanswer['stop'])
        if stop < start:
            start, stop = stop, start
        # end if
        return self.crawler.chapters[start:(stop + 1)]
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
        return self.crawler.chapters[start:(stop + 1)]
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
        return [
            chap for chap in self.crawler.chapters
            if selected.count(chap['volume']) > 0
        ]
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
        return [
            chap for chap in self.crawler.chapters
            if selected.count(chap['id']) > 0
        ]
    # end def

    def additional_configs(self):
        answer = prompt([
            # {
            #     'type': 'checkbox',
            #     'name': 'formats',
            #     'choices': [
            #        { 'name': 'JSON', 'checked': True },
            #        { 'name': 'EPUB', 'checked': True },
            #        { 'name': 'MOBI', 'checked': True  },
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
                'name': 'volume',
                'message': 'Generate separate files for each volumes?',
                'default': True,
            },
        ])
        # self.formats = answer['formats']
        self.pack_by_volume = answer['volume']
    # end def

    def download_chapters(self):
        if self.crawler.novel_cover is not None:
            logger.warn('Getting cover image...')
            try:
                filename = self.crawler.novel_cover.split('/')[-1]
                filename = os.path.join(self.output_path, filename)
                self.book_cover = filename
                if not os.path.exists(self.book_cover):
                    logger.info('Downloading cover image')
                    retrieve_image(self.crawler.novel_cover, filename)
                    logger.info('Saved cover: %s', filename)
                # end if
            except Exception as ex:
                self.book_cover = None
                logger.error('Failed to get cover: %s', ex)
            # end try
        else:
            logger.warn('No cover image.')
        # end if

        bar = IncrementalBar('Downloading chapters', max=len(self.chapters))
        bar.start()
        futures_to_check = {
            self.crawler.executor.submit(
                self.download_chapter_body, chapter): chapter['id']
            for chapter in self.chapters
        }
        for future in futures.as_completed(futures_to_check):
            result = future.result()
            if result:
                bar.clearln()
                logger.error(result)
            # end if
            bar.next()
        # end for
        bar.finish()
    # end def

    def download_chapter_body(self, chapter):
        result = None

        dir_name = os.path.join(self.output_path, 'json')
        if self.pack_by_volume:
            dir_name = os.path.join(dir_name, chapter['volume'])
        # end if
        os.makedirs(dir_name, exist_ok=True)

        chapter_name = str(chapter['id']).rjust(5, '0')
        file_name = os.path.join(dir_name, chapter_name + '.json')

        chapter['body'] = ''
        if os.path.exists(file_name):
            logger.info('Restoring from %s', file_name)
            with open(file_name, 'r') as file:
                old_chapter = json.load(file)
                chapter['body'] = old_chapter['body']
            # end with
        if len(chapter['body']) == 0:
            logger.info('Downloading to %s', file_name)
            body = self.crawler.download_chapter_body(chapter)
            if len(body) == 0:
                result = 'Body is empty: ' + chapter['url']
            else:
                chapter['body'] = '<h3>%s</h3><h1>%s</h1>\n%s' % (
                    chapter['volume'], chapter['title'], body)
            # end if
            with open(file_name, 'w') as file:
                file.write(json.dumps(chapter))
            # end with
        # end if

        return result
    # end def

    def bind_books(self):
        if self.pack_by_volume:
            for i, vol in enumerate(self.crawler.volumes):
                chapters = [
                    x for x in self.chapters
                    if x['volume'] == vol['title'] and len(x['body']) > 0
                ]
                if len(chapters) > 0:
                    bind_epub_book(
                        self,
                        chapters=chapters,
                        volume='Volume %d' % (i + 1),
                    )
                # end if
            # end for
        else:
            bind_epub_book(
                self,
                chapters=self.chapters,
            )
        # end if

        novel_to_mobi(self.output_path)
    # end def
# end class
