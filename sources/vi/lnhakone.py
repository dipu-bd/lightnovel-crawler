# -*- coding: utf-8 -*-
import logging
import re
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = '%s/tim-kiem-nang-cao?title=%s'
chapter_list_url = 'https://listnovel.com/wp-admin/admin-ajax.php'


class ListNovelCrawler(Crawler):
    machine_translation = True
    base_url = [
        'https://ln.hako.re/',
        'https://docln.net/',
    ]

    def initialize(self):
        self.executor = ThreadPoolExecutor(1)
    # end def

    def search_novel(self, query):
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % (self.home_url, query))

        results = []
        for tab in soup.select('.sect-body .thumb-item-flow'):
            a = tab.select_one('.series-title a')
            latest_vol = tab.select_one('.volume-title').text.strip()
            latest_chap = tab.select_one('.chapter-title a')['title']
            results.append({
                'title': a['title'],
                'url': self.absolute_url(a['href']),
                'info': '%s | %s' % (latest_vol, latest_chap),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.series-name a').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = ' '.join([a.text.strip() for a in soup.select('.info-value a[href*="/tac-gia/"]')])
        logger.info('%s', self.novel_author)

        possible_image = soup.select_one('.series-cover .img-in-ratio')['style']
        possible_image = re.findall(r"url\('([^']+)'\)", possible_image)
        self.novel_cover = self.absolute_url(possible_image[0])
        logger.info('Novel cover: %s', self.novel_cover)

        for section in soup.select('.volume-list'):
            vol_id = 1 + len(self.volumes)
            vol_title = section.select_one('.sect-title').text.strip()
            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })
            for a in section.select('.list-chapters a'):
                chap_id = 1 + len(self.chapters)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a['title'],
                    'url': self.absolute_url(a['href']),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('#chapter-content p')
        return ''.join([str(p) for p in contents])
    # end def
# end class
