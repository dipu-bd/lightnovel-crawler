# -*- coding: utf-8 -*-
import logging
import re
from bs4 import BeautifulSoup
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

ajaxchapter_url = 'https://www.1ksy.com/home/index/ajaxchapter'


class OneKsyCrawler(Crawler):
    base_url = [
        'https://m.1ksy.com/',
        'https://www.1ksy.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.1ksy.com/'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace(
            'https://m.1ksy', 'https://www.1ksy')
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        self.novel_title = soup.select_one(
            'body > div.jieshao > div.rt > h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('body > div > div.lf > img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one(
            'meta[property="og:novel:author"]')['content']
        logger.info('Novel author: %s', self.novel_author)

        chap_id = 0
        for a in soup.select('body > div.mulu ul')[-1].select('li a'):
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
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('#content')
        return self.extract_contents(contents)
    # end def
# end class