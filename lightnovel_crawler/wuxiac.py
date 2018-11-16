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

        self.novel_title = soup.select_one('#maininfo h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('#maininfo p').text.strip()
        self.novel_author = re.sub(r'^Author[^\w]+', '', self.novel_author).strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = soup.select_one('#sidebar img')['src']
        if not re.search(r'^https?://', self.novel_cover):
            self.novel_cover = home_url + self.novel_cover
        # end if
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        volume = { 'id': 0, 'title': 'Volume 1', }
        for item in soup.select('#list dl *'):
            if item.name == 'dt':
                vol = volume.copy()
                vol['id'] += 1
                vol['title'] = item.text.strip()
                vol['title'] = re.sub(r'^(.*)', '', vol['title'])
                vol['title'] = re.sub(r'^\s*Text\s*$', '', vol['title']).strip()
                volume = vol
            # end if
            if item.name == 'dd':
                a = item.select_one('a')
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': volume['id'],
                    'url':  url + a['href'],
                    'title': a.text.strip(),
                })
                if last_vol != volume['id']:
                    last_vol = volume['id']
                    self.volumes.append(volume)
                # end if
            # end if
        #end for

        logger.debug(self.volumes)
        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        body_parts = soup.select_one('div#content').contents
        body = []
        for elem in body_parts:
            if not elem.name:
                text = str(elem).strip()
                if len(body) == 0 and self.is_blacklisted(text):
                    continue
                # end if
                if len(text) > 0:
                    body.append(text)
                # end if
            # end if
        # end for
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

    def is_blacklisted(self, text):
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
