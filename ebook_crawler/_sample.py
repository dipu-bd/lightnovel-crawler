#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Use this sample to create new sources
"""
import json
import logging
import re
import requests
from concurrent import futures
from .app.parser import Parser
from .app.crawler import Crawler
from .app.crawler_app import CrawlerApp

logger = logging.getLogger('CHANGE_THIS_NAME')

class SampleParser(Parser):
    def get_title(self):
        pass
    # end def

    def get_authors(self):
        pass
    # end def

    def get_cover(self):
        pass
    # end def

    def get_volumes(self):
        pass
    # end def

    def get_chapters(self):
        pass
    # end def

    def get_chapter_body(self):
        pass
    # end def
# end class


class SampleCrawler(Crawler):
    @property
    def supports_login(self):
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self):
        pass
    # end def

    def download_chapter(self, url):
        pass
    # end def
# end class


class SampleCrawlerApp(CrawlerApp):
    crawler = SampleCrawler()
# end class


if __name__ == '__main__':
    SampleCrawlerApp().start()
# end if
