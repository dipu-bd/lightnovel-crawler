#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for novels from [LNMTL](https://lnmtl.com).
"""
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger('PARSER')


class Parser:
    def __init__(self, html):
        self.soup = BeautifulSoup(html, 'lxml')
    # end def

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

    def print_body(self):
        logger.debug('-' * 80)
        body = self.soup.select_one('body').text
        logger.debug('\n\n'.join(
            [x for x in body.split('\n\n') if len(x.strip())]))
        logger.debug('-' * 80)
    # end def
# end class
