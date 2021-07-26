# -*- coding: utf-8 -*-
import json
import logging
import re
from urllib.parse import urlparse

import requests

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = 'https://read.aixdzs.com/%s'


class AixdzsCrawler(Crawler):
    base_url = 'https://www.aixdzs.com'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        if not self.novel_url.endswith('/'):
            self.novel_url += '/'
        # end if
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_cover = soup.select_one(
            'meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_title = soup.select_one(
            'meta[property="og:novel:book_name"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            'meta[property="og:novel:author"]')['content']
        logger.info('%s', self.novel_author)

        parsed_url = urlparse(self.novel_url)
        parsed_path = parsed_url.path.strip('/').split('/')
        chapter_url = chapter_list_url % ('/'.join(parsed_path[1:]))
        logger.debug('Visiting %s', chapter_url)
        soup = self.get_soup(chapter_url)

        volumes = set([])
        for a in reversed(soup.select('div.catalog li a')):
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'title': a.text,
                'url': self.absolute_url(a['href'], page_url=chapter_url),
            })
        # end def

        self.volumes = [{'id': x, 'title': ''} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('.content > p')
        contents = [str(p) for p in contents if p.text.strip()]
        return ''.join(contents)
    # end def
# end class
