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


class WuxiaComCrawler(Crawler):
    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.com/'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace('https://m', 'https://www')
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.novel_title = soup.select_one('.section-content  h4').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('img.media-object')['src'])
            logger.info('Novel cover: %s', self.novel_cover)
        except Exception as ex:
            logger.debug('Failed to get cover: %s', ex)
        # end try

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
                    'url': self.absolute_url(a['href']),
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

        self.blacklist_patterns = [
            r'^<span>(...|\u2026)</span>$',
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        body_parts = soup.select_one('.panel-default .fr-view')
        body = self.extract_contents(body_parts.contents)
        return '<p>' + '</p><p>'.join(body) + '</p'
    # end def
# end class
