#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [Wuxia World Online](https://wuxiaworld.online/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('WUXIA_ONLINE')


class WuxiaOnlineCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        # self.novel_author = soup.select_one('#maininfo p').text.strip()
        # self.novel_author = re.sub(r'^Author[^\w]+', '', self.novel_author).strip()
        # logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.info_image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        for a in reversed(soup.select('.chapter-list .row span a')):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + (chap_id - 1) // 100
            volume = {'id': vol_id, 'title': ''}
            if last_vol != vol_id:
                self.volumes.append(volume)
                last_vol = vol_id
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url':  self.absolute_url(a['href']),
            })
        # end for

        logger.debug(self.volumes)
        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        parts = soup.select_one('#list_chapter .content-area')
        body = self.extract_contents(parts.contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
