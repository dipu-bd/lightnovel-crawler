#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use this sample to create new sources
"""
import json
import logging
import re
from concurrent import futures

from .app.crawler import Crawler
from .app.crawler_app import CrawlerApp

logger = logging.getLogger('CHANGE_THIS_NAME')


class SampleCrawler(Crawler):
    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        '''Login and update cookies in `headers`'''
        pass
    # end def

    def logout(self):
        '''Logout and update cookies in `headers`'''
        pass
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        pass
    # end def

    def download_chapter_list(self):
        '''Download list of chapters and volumes.'''
        pass

    def download_chapter_body(self, url):
        '''Download body of a single chapter and return as clean html format.'''
        pass
    # end def
# end class


class SampleCrawlerApp(CrawlerApp):
    crawler = SampleCrawler()
# end class


if __name__ == '__main__':
    SampleCrawlerApp().start()
# end if
