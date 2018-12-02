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
from .prompts import (download_selection, login_info, pack_by_volume,
                      range_from_chapters, range_from_volumes,
                      range_using_index, range_using_urls)


class Program:
    crawler = Crawler()
    logger = logging.getLogger('CRAWLER_APP')

    def run(self, crawler):
        self.crawler = crawler
        self.pack_by_volume = False

        self.crawler.initialize()

        if self.crawler.supports_login:
            data = login_info()
            if data and len(data) == 2:
                crawler.login(data[0], data[1])
            # end if
        # end if

        novel_info(self)

        if len(self.crawler.volumes) > 0:
            self.pack_by_volume = pack_by_volume()
        # end if
        self.logger.info('To be packed by volume = %s', self.pack_by_volume)

        self.chapter_range()
        download_chapters(self)

        if self.crawler.supports_login:
            self.crawler.logout()
        # end if

        bind_books(self)

        self.crawler.dispose()
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
