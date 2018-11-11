#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
The main entry point of the program
"""
import logging
from ..utils.crawler import Crawler

from .login import login
from .novel_info import novel_info
from .chapter_range import chapter_range
from .additional_configs import additional_configs
from .download_chapters import download_chapters
from .bind_books import bind_books

class Program:
    crawler = Crawler()
    logger = logging.getLogger('CRAWLER_APP')

    def run(self, crawler):
        self.crawler = crawler

        self.crawler.initialize()

        if self.crawler.supports_login:
            login(crawler)
        # end if

        novel_info(self)
        chapter_range(self)
        additional_configs(self)
        download_chapters(self)

        if self.crawler.supports_login:
            self.crawler.logout()
        # end if

        bind_books(self)

        self.crawler.dispose()
    # end def
# end class
