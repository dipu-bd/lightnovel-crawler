#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import logging
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('WEBNOVEL_ONLINE')

class WebnovelOnlineCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        img = soup.select_one('main img.cover')
        self.novel_title = img['title'].strip()
        self.novel_cover = self.absolute_url(img['src'])
        
        span = soup.select_one('header span.send-author-event')
        if span:
            self.novel_author = span.text.strip()
        # end if

        chap_id = 0
        for a in soup.select('#info a.on-navigate-part'):
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
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        strong = soup.select_one('#story-content strong')
        if strong and re.search(r'Chapter \d+', strong.text):
            chapter['title'] = strong.text.strip()
            logger.info('Updated title: %s', chapter['title'])
        # end if

        body_parts = soup.select_one('#story-content')
        for x in body_parts.select('h1, h3, hr'):
            x.decompose()
        # end for
        body = self.extract_contents(body_parts.contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
