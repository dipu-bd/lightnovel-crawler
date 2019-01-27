#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import shutil
import logging

from ..spiders import crawler_list
from ..binders import bind_books
from .downloader import download_chapters
from .novel_info import format_volumes, format_chapters, save_metadata


logger = logging.getLogger('APP')


class App:
    progress = 0
    user_input = None
    crawler_links = None
    crawler = None
    login_data = ()
    search_results = []
    output_path = None
    pack_by_volume = False
    chapters = []
    book_cover = None
    output_formats = None
    archived_output = None

    # ----------------------------------------------------------------------- #

    def initialize(self):
        logger.info('Initialized App')
    # end def

    def destroy(self):
        if self.crawler:
            self.crawler.destroy()
        # end if
        logger.info('Destroyed App')
    # end def

    # ----------------------------------------------------------------------- #

    def init_search(self):
        '''Requires: user_input'''
        '''Produces: [crawler, output_path] or [crawler_links]'''
        if not self.user_input:
            raise Exception('User input is not valid')
        # end if

        if self.user_input.startswith('http'):
            logger.info('Detected URL input')
            self.init_crawler(self.user_input)
        else:
            logger.info('Detected query input')
            self.crawler_links = [
                link for link in sorted(crawler_list.keys())
                if 'search_novel' in crawler_list[link].__dict__
            ]
        # end if
    # end def

    def search_novel(self):
        '''Requires: user_input, crawler_links'''
        '''Produces: search_results'''
        logger.warn('Searching for novels in %d sites...',
                    len(self.crawler_links))
        _checked = {}
        self.search_results = []
        for link in self.crawler_links:
            logger.info('Searching: %s with "%s"', link, self.user_input)
            try:
                crawler = crawler_list[link]
                if crawler in _checked:
                    continue
                # end if
                _checked[crawler] = True

                instance = crawler()
                instance.home_url = link.strip('/')
                results = instance.search_novel(self.user_input)
                self.search_results += results
                logger.debug(results)
                logger.info('%d results from %s', len(results), link)
            except Exception as ex:
                logger.debug(ex)
            # end try
        # end for
        if len(self.search_results) == 0:
            raise Exception('No results for: %s' % self.user_input)
        # end if
        logger.info('Total %d novels found from %d sites',
                    len(self.search_results), len(self.crawler_links))
    # end def

    # ----------------------------------------------------------------------- #

    def init_crawler(self, novel_url):
        '''Requires: [user_input]'''
        '''Produces: crawler'''
        if not novel_url:
            return
        for home_url, crawler in crawler_list.items():
            if novel_url.startswith(home_url):
                logger.info('Initializing crawler for: %s', home_url)
                self.crawler = crawler()
                self.crawler.novel_url = novel_url
                self.crawler.home_url = home_url.strip('/')
                break
            # end if
        # end for
        if not self.crawler:
            raise Exception('No crawlers were found')
        # end if
    # end def

    @property
    def can_login(self):
        return 'login' in self.crawler.__dict__
    # end def

    def get_novel_info(self):
        '''Requires: crawler, login_data'''
        '''Produces: output_path'''
        self.crawler.initialize()

        if self.can_login and self.login_data:
            self.crawler.login(*self.login_data)
        # end if

        logger.warn('Retrieving novel info...')
        self.crawler.read_novel_info()
        logger.warn('NOVEL: %s', self.crawler.novel_title)

        logger.info('Getting chapters...')
        self.crawler.download_chapter_list()

        format_volumes(self.crawler)
        format_chapters(self.crawler)

        good_name = re.sub(r'[\\/*?:"<>|\']', '', self.crawler.novel_title)
        self.output_path = os.path.join('Lightnovels', good_name)
    # end def

    # ------------------------------------------------------------------------#
    def start_download(self):
        '''Requires: crawler, chapters, output_path'''
        if not os.path.exists(self.output_path):
            raise Exception('Output path is not defined')
        # end if

        save_metadata(self.crawler, self.output_path)
        download_chapters(self)
    
        if 'logout' in self.crawler.__dict__:
            self.crawler.logout()
        # end if
    # end def

    # ------------------------------------------------------------------------#

    def bind_books(self):
        '''Requires: crawler, chapters, output_path, pack_by_volume, book_cover, output_formats'''
        logger.info('Processing data for binding')
        data = {}
        if self.pack_by_volume:
            for vol in self.crawler.volumes:
                data['Volume %d' % vol['id']] = [
                    x for x in self.chapters
                    if x['volume'] == vol['id']
                    and len(x['body']) > 0
                ]
            # end for
        else:
            data[''] = self.chapters
        # end if

        bind_books(self, data)
    # end def

    # ------------------------------------------------------------------------#

    def compress_output(self):
        logger.info('Compressing output...')
        self.archived_output = shutil.make_archive(self.output_path, 'zip', self.output_path)
        logger.warn('Compressed to %s' % self.archived_output)
    # end def
# end class
