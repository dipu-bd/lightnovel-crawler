# -*- coding: utf-8 -*-
from lncrawl.core.crawler import Crawler
import requests
import re
import logging
import json

logger = logging.getLogger(__name__)


class ChineseFantasyNovels(Crawler):
    base_url = 'https://m.chinesefantasynovels.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        if not self.novel_url.endswith('/'):
            self.novel_url += '/'
        # end if
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.btitle h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('.bookinfo .status').text
        logger.info('%s', self.novel_author)

        volumes = set([])
        for a in reversed(soup.select('dl.chapterlist a')):
            ch_title = a.text.strip()
            ch_id = [int(x) for x in re.findall(r'\d+', ch_title)]
            ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'title': ch_title,
                'url': self.absolute_url(a['href']),
            })
        # end def

        self.volumes = [{'id': x, 'title': ''} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('#BookText')
        self.bad_css += ['.link']
        return self.extract_contents(content)
    # end def
# end class
