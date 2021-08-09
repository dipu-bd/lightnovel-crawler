# -*- coding: utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://wuxiaworld.co/search/{}/1'


class WuxiaCoCrawler(Crawler):
    base_url = [
        'https://www.wuxiaworld.co/',
        'https://m.wuxiaworld.co/',
    ]

    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.co/'
        self.executor = ThreadPoolExecutor(max_workers=1)
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        url = search_url.format(query.lower())
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        results = []
        for li in soup.select('ul.result-list li'):
            a = li.select_one('a.book-name')['href']
            author = li.select_one('a.book-name font').text
            title = li.select_one('a.book-name').text.replace(author,"")

            results.append({
                'title': title,
                'url': self.absolute_url(a),
                'info': author,
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url.replace('https://m', 'https://www')
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        self.novel_title = soup.select_one('div.book-name').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('div.author span.name').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.book-img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('ul.chapter-list a')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  self.absolute_url(a['href']),
                'title': a.select_one('p.chapter-name').text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        chapter['title'] = soup.select_one('h1.chapter-title').text.strip()

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        body_parts = soup.select_one('div.chapter-entity')
        
        return self.extract_contents(body_parts)
    # end def
# end class
