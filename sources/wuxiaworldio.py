# -*- coding: utf-8 -*-
import logging
import re
from bs4 import BeautifulSoup
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://wuxiaworld.io/search.ajax?type=&query=%s'

class WuxiaWorldIo(Crawler):
    base_url = [
        'https://wuxiaworld.io/',
        'https://wuxiaworld.name/',
    ]

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        soup = self.get_soup(search_url % query)

        results = []
        for novel in soup.select('li'):
            a = novel.select_one('.resultname a')
            info = novel.select_one('a:nth-of-type(2)')
            info = info.text.strip() if info else ''
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': 'Latest: %s' % info,
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        # self.novel_title = soup.select_one('h1.entry-title').text.strip()
        self.novel_title = soup.select_one('div.entry-header h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('span.info_image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('div.truyen_info_right li')[1].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        for a in reversed(soup.select('#list_chapter .chapter-list a')):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
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
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        if 'Chapter' in soup.select_one('h1').text:
            chapter['title'] = soup.select_one('h1').text
        else:
            chapter['title'] = chapter['title']
        # end if

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.select_one('div.content-area')
        return self.extract_contents(contents)
    # end def
# end class