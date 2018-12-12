#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The main entry point of the program
"""
import logging

from ..binders import bind_books
from ..utils.crawler import Crawler
from .arguments import get_args
from .downloader import download_chapters
from .novel_info import novel_info
from .display import url_not_recognized
from .prompts import (choose_a_novel, download_selection,
                      get_crawlers_to_search, get_novel_url, login_info,
                      pack_by_volume, range_from_chapters, range_from_volumes,
                      range_using_index, range_using_urls)

logger = logging.getLogger('CRAWLER_APP')


class Program:
    '''Initiate the app'''

    def __init__(self, *args, **kwargs):
        self.logger = logger
        self.crawler = Crawler()
        self.pack_by_volume = False
    # end def

    @classmethod
    def run(cls, choice_list):
        app = cls()
        app.get_crawler_instance(choice_list)
        if not app.crawler:
            url_not_recognized(choice_list)
            raise Exception('No crawlers are available for it yet')
        # end if

        app.crawler.initialize()

        if 'login' in app._methods:
            data = login_info()
            if data and len(data) == 2:
                app.crawler.login(data[0], data[1])
            # end if
        # end if

        novel_info(app)

        if len(app.crawler.volumes) > 0:
            app.pack_by_volume = pack_by_volume()
        # end if
        logger.info('To be packed by volume = %s', app.pack_by_volume)

        app.chapter_range()
        download_chapters(app)

        if 'logout' in app._methods:
            app.crawler.logout()
        # end if

        bind_books(app)

        app.crawler.dispose()
    # end if

    def get_crawler_instance(self, choice_list):
        novel = get_novel_url()

        if not novel.startswith('http'):
            search_results = []
            crawler_links = get_crawlers_to_search([
                x for x in sorted(choice_list.keys())
                if 'search_novel' in choice_list[x].__dict__
            ])
            _checked = {}
            logger.warn('Searching for novels in %d sites...',
                        len(crawler_links))
            for link in crawler_links:
                logger.info('Searching %s', link)
                try:
                    crawler = choice_list[link]
                    if crawler in _checked:
                        continue
                    # end if
                    _checked[crawler] = True
                    instance = crawler()
                    instance.home_url = link.strip('/')
                    results = instance.search_novel(novel)
                    search_results += results
                    logger.debug(results)
                    logger.info('%d results found', len(results))
                except Exception as ex:
                    logger.debug(ex)
                # end try
            # end for
            if len(search_results) == 0:
                raise Exception('No results for: %s' % novel)
            # end if
            novel = choose_a_novel(search_results)
        # end if

        if not novel:
            raise Exception('Novel URL was not specified')
        # end if
        for home_url, crawler in choice_list.items():
            if novel.startswith(home_url):
                self.crawler = crawler()
                self.crawler.novel_url = novel
                self.crawler.home_url = home_url.strip('/')
                self._methods = crawler.__dict__
                break
            # end if
        # end for
    # end def

    def chapter_range(self):
        chapter_count = len(self.crawler.chapters)
        volume_count = len(self.crawler.volumes)
        res = download_selection(chapter_count, volume_count)

        arg = get_args()
        self.chapters = []
        if res == 'all':
            self.chapters = self.crawler.chapters[:]
        elif res == 'first':
            n = arg.first or 10
            self.chapters = self.crawler.chapters[:n]
        elif res == 'last':
            n = arg.last or 10
            self.chapters = self.crawler.chapters[-n:]
        elif res == 'page':
            start, stop = range_using_urls(self.crawler)
            self.chapters = self.crawler.chapters[start:(stop + 1)]
        elif res == 'range':
            start, stop = range_using_index(chapter_count)
            self.chapters = self.crawler.chapters[start:(stop + 1)]
        elif res == 'volumes':
            selected = range_from_volumes(self.crawler.volumes)
            self.chapters = [
                chap for chap in self.crawler.chapters
                if selected.count(chap['volume']) > 0
            ]
        elif res == 'chapters':
            selected = range_from_chapters(self.crawler)
            self.chapters = [
                chap for chap in self.crawler.chapters
                if selected.count(chap['id']) > 0
            ]
        # end if

        if not len(self.chapters):
            self.logger.error('No chapters was selected')
            raise Exception()
        # end if

        self.logger.debug('Selected chapters to download:')
        self.logger.debug(self.chapters)
        self.logger.info('%d chapters to be downloaded', len(self.chapters))
    # end def
# end class
