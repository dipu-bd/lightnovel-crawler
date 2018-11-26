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

home_url = 'https://wuxiaworld.online'

class WuxiaOnlineCrawler(Crawler):
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

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        # self.novel_author = soup.select_one('#maininfo p').text.strip()
        # self.novel_author = re.sub(r'^Author[^\w]+', '', self.novel_author).strip()
        # logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = soup.select_one('.info_image img')['src']
        if not re.search(r'^https?://', self.novel_cover):
            self.novel_cover = home_url + self.novel_cover
        # end if
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        for a in reversed(soup.select('.chapter-list .row span a')):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + (chap_id - 1) // 100
            volume = { 'id': vol_id, 'title': '' }
            if last_vol != vol_id:
                self.volumes.append(volume)
                last_vol = vol_id
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  a['href'],
                'title': a['title'],
            })
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

        parts = soup.select_one('#list_chapter .content-area')
        body = self.extract_text_from(parts.contents)
        body = [x for x in body if len(x) and self.not_blacklisted(x)]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

    def extract_text_from(self, contents):
        body = []
        for elem in contents:
            if not elem.name:
                body.append(str(elem).strip())
            elif ['p', 'div'].count(elem.name):
                body += self.extract_text_from(elem.contents)
            elif ['strong', 'p', 'span', 'b', 'i'].count(elem.name):
                body.append(elem.text.strip())
            # end if
        # end for
        return body
    # end def

    def not_blacklisted(self, text):
        blacklist = [
            # r'^(...|\u2026)$',
            r'^(edit|translat)(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        for item in blacklist:
            if re.search(item, text, re.IGNORECASE):
                return False
            # end if
        # end for
        return True
    # end def
# end class
