#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('ROMANTIC_LOVE_BOOKS')

class RomanticLBCrawler(Crawler):
    def initialize(self):
        self.home_url = 'https://m.romanticlovebooks.com'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace('https://www', 'https://m')
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')
        
        self.novel_title = soup.select_one('.pt-novel .pt-name').text.strip()
        self.novel_cover = self.absolute_url(
            soup.select_one('.baseinfo img')['src'])
        
        for info in soup.select('.pt-novel .pt-info'):
            text = info.text.strip()
            if text.lower().startswith('author'):
                self.novel_author = text
                break
            # end if
        # end for

        chap_id = 0
        for a in soup.select('#chapterlist li a'):
            vol_id = chap_id // 100 + 1
            if vol_id > len(self.volumes):
                self.volumes.append({
                    'id': vol_id,
                    'title': 'Volume %d' % vol_id
                })
            # end if

            chap_id += 1
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        body_parts = soup.select_one('div#BookText').contents
        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
