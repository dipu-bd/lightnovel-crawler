#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [WuxiaWorld](http://www.wuxiaworld.com/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('WUXIA_WORLD')

home_url = 'https://www.wuxiaworld.com'

class WuxiaCrawler(Crawler):
    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.novel_title = soup.select_one('.section-content  h4').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = soup.select_one('img.media-object')['src']
            if not re.search(r'^https?://', self.novel_cover):
                self.novel_cover = home_url + self.novel_cover
            # end if
        except Exception as ex:
            logger.debug('Failed to get cover: %s', ex)
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one('.media-body dl dt').text
        self.novel_author += soup.select_one('.media-body dl dd').text
        logger.info('Novel author: %s', self.novel_author)

        for panel in soup.select('#accordion .panel-default'):
            vol_id = int(panel.select_one('h4.panel-title .book').text)
            vol_title = panel.select_one('h4.panel-title .title a').text
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })
            for a in panel.select('ul.list-chapters li.chapter-item a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url': home_url + a['href'],
                    'title': a.text.strip() or ('Chapter %d' % chap_id),
                })
            # end def
        # end def

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        body_parts = []
        beginner = True
        for item in soup.select('.panel-default .fr-view *'):
            if item.name == 'hr':
                beginner = False
            text = item.text.strip()
            if item.name != 'p' or text == '':
                continue
            if beginner and self.check_blacklist(text):
                continue
            beginner = False
            body_parts.append(str(item.extract()))
        # end for
        return ''.join(body_parts).strip()
    # end def

    def check_blacklist(self, text):
        blacklist = [
            r'^(...|\u2026)$',
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        for item in blacklist:
            if re.search(item, text, re.IGNORECASE):
                return True
            # end if
        # end for
        return False
    # end def
# end class
