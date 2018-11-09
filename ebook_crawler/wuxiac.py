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

home_url = 'https://www.wuxiaworld.co/'

class WuxiaCoCrawler(Crawler):
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

        self.novel_title = soup.select_one('h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = home_url + soup.find('img')['src']
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.find_all('p')[1].text
        self.novel_author = author.lstrip('Author：')
        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('dd a'):
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id =  chap_id//100 +1
                vol_title =  'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            #end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  url + a['href'],
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        #end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        body_parts = soup.find("div", {"id": "content"})
        body_parts.script.decompose()

        return body_parts
    # end def
# end class
