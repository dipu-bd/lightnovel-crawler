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
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one('.detail-info .col-image img')

        self.novel_title = image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        any_chapter_url = soup.select_one('.chapter a[href*="/novel/"]')['href']
        soup = self.get_soup(any_chapter_url)

        volumes = set([])
        for option in soup.select('select.select-chapter option'):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)
            option['value']
            option.text.strip()
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': option.text.strip(),
                'url': self.absolute_url(option['value']),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.reading-detail .container')
        self.bad_css += ['h1', 'h2', 'h3', 'h4']
        return self.extract_contents(contents)
    # end def
# end class
