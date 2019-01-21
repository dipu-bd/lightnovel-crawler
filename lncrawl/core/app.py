#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import logging

from . import display
from ..spiders import crawler_list
from ..binders import bind_books
from .downloader import download_chapters
from .novel_info import format_volumes, format_chapters, save_metadata


logger = logging.getLogger('APP')


class App:
    _methods = {}
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

    # ------------------------------------------------------------------------#

    def initialize(self):
        logger.info('Initialized')
    # end def

    def destroy(self):
        self.crawler.destroy()
        logger.info('Destroyed')
    # end def

    # ------------------------------------------------------------------------#

    def init_search(self):
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
        logger.warn('Searching for novels in %d sites...',
                    len(self.crawler_links))
        _checked = {}
        self.search_results = []
        for link in self.crawler_links:
            logger.info('Searching %s', link)
            try:
                crawler = crawler_list[link]
                if crawler in _checked:
                    continue
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

    # ------------------------------------------------------------------------#

    def init_crawler(self, novel_url):
        if not novel_url: return
        for home_url, crawler in crawler_list.items():
            if novel_url.startswith(home_url):
                logger.info('Initializing crawler for: %s', home_url)
                self.crawler = crawler()
                self.crawler.novel_url = self.user_input
                self.crawler.home_url = home_url.strip('/')
                self.crawler.initialize()
                break
            # end if
        # end for
        if not self.crawler:
            display.url_not_recognized()
            raise Exception('No crawlers were found')
        # end if
        good_name = re.sub(r'[\\/*?:"<>|\']', '', self.crawler.novel_title)
        self.output_path = os.path.join('Lightnovels', good_name)
    # end def

    def can_login(self):
        return 'login' in self.crawler.__dict__
    # end def

    def get_novel_info(self):
        if self.can_login() and self.login_data:
            self.crawler.login(*self.login_data)
        # end if
        if not os.path.exists(self.output_path):
            raise Exception('Output path is not defined')
        # end if

        logger.warn('Retrieving novel info...')
        self.crawler.read_novel_info()
        logger.warn('NOVEL: %s', self.crawler.novel_title)

        logger.info('Getting chapters...')
        self.crawler.download_chapter_list()

        format_volumes(self.crawler)
        format_chapters(self.crawler)
        save_metadata(self.crawler, self.output_path)
    # end def

    # ------------------------------------------------------------------------#
    def start_download(self):
        download_chapters(self)
        if 'logout' in self.crawler.__dict__:
            self.crawler.logout()
        # end if
    # end def

    # ------------------------------------------------------------------------#

    def bind_books(self):
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
# end class
