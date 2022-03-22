# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = ' https://novelfullplus.com/ajax/search?q=%s'

RE_VOLUME = r'(?:book|vol|volume) (\d+)'


class NovelFullPlus(Crawler):
    base_url = 'https://novelfullplus.com/'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(['h1', 'h2', 'h3', 'h4'])
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('ul li a'):
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        self.novel_url = self.novel_url.split('#')[0]
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one('.books .book img')

        self.novel_title = image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        split_url = self.novel_url.split('/')
        self.novel_id = split_url[len(split_url)-1]
        logger.info('Novel id: %s', self.novel_id)

        chapters_soup = self.get_soup('https://novelfullplus.com/ajax/chapter-archive?novelId=' +  self.novel_id)

        volumes = set([])
        for a in chapters_soup.select('.list-chapter li a'):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'].strip(),
                'url': self.absolute_url(a['href'].strip()),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('#chr-content')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
