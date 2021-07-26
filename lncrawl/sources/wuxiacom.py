# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = 'https://www.wuxiaworld.com/novel/%s'
search_url = 'https://www.wuxiaworld.com/api/novels/search?query=%s&count=5'


class WuxiaComCrawler(Crawler):
    base_url = ['https://www.wuxiaworld.com/']

    def initialize(self):
        self.home_url = 'https://www.wuxiaworld.com'
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        url = search_url % query
        logger.info('Visiting %s ...', url)
        data = self.get_json(url)
        # logger.debug(data)

        results = []
        for item in data['items'][:5]:
            results.append({
                'title': item['name'],
                'url': book_url % item['slug'],
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        self.novel_id = self.novel_url.split(
            'wuxiaworld.com/novel/')[1].split('/')[0]
        logger.info('Novel Id: %s', self.novel_id)

        self.novel_url = book_url % self.novel_id
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.section-content h2').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('img.media-object')['src'])
            logger.info('Novel cover: %s', self.novel_cover)
        except Exception:
            logger.debug('Failed to get cover: %s', self.novel_url)
        # end try

        authors = ''
        for d in soup.select_one('.media-body dl, .novel-body').select('dt, dd'):
            authors += d.text.strip()
            authors += ' ' if d.name == 'dt' else '; '
        # end for
        self.novel_author = authors.strip().strip(';')
        logger.info('Novel author: %s', self.novel_author)

        for panel in soup.select('#accordion .panel-default'):
            vol_id = int(panel.select_one('h4.panel-title .book').text)
            vol_title = panel.select_one('h4.panel-title .title a').text
            if re.search(r'table of contents', vol_title, flags=re.I):
                vol_title = 'Volume %s' % vol_id
            # end if
            self.volumes.append({
                'id': vol_id,
                'title': vol_title.strip(),
            })
            for a in panel.select('ul.list-chapters li.chapter-item a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'url': self.absolute_url(a['href']),
                    'title': a.text.strip(),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body = soup.select_one('#chapterContent')
        if not body:
            body = soup.select_one('#chapter-content')
        # end if
        if not body:
            body = soup.select_one('.panel-default .fr-view')
        # end if
        if not body:
            return ''
        # end if

        for nav in (soup.select('.chapter-nav') or []):
            nav.extract()
        # end for

        self.blacklist_patterns = [
            r'^<span>(...|\u2026)</span>$',
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        return self.extract_contents(body)
    # end def
# end class
