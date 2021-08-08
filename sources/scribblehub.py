# -*- coding: utf-8 -*-
import json
import logging
import re
from urllib.parse import quote
from lncrawl.core.crawler import Crawler
from math import ceil

logger = logging.getLogger(__name__)
search_url = 'https://www.scribblehub.com/?s=%s&post_type=fictionposts'


class ScribbleHubCrawler(Crawler):
    base_url = 'https://www.scribblehub.com/'

    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        results = []
        for novel in soup.select('div.search_body'):
            a = novel.select_one('.search_title a')
            info = novel.select_one('.search_stats').text.strip()
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': info,
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find('div', {'class': 'fic_title'})[
            'title'].strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('div', {'class': 'fic_image'}).find('img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find(
            'span', {'class': 'auth_name_fic'}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapter_count = soup.find('span', {'class': 'cnt_toc'}).text
        chapter_count = -1 if not chapter_count else int(chapter_count)
        page_count = ceil(chapter_count/15)
        logger.info('Chapter list pages: %d' % page_count)

        logger.info('Getting chapters...')
        chapters = []
        for i in range(page_count):
            chapters.extend(self.download_chapter_list(i+1))
        # end for
        for x in reversed(chapters):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters)//100 + 1
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        self.volumes = [
            {'id': x + 1}
            for x in range(len(self.chapters) // 100 + 1)
        ]
    # end def

    def download_chapter_list(self, page):
        '''Download list of chapters and volumes.'''
        url = self.novel_url.split('?')[0].strip('/')
        url += '?toc=%s#content1' % page
        soup = self.get_soup(url)
        logger.debug('Crawling chapters url in page %s' % page)
        return soup.select('a.toc_a')
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.find('div', {'id': 'chp_raw'})

        #body_parts = []
        # for x in contents:
        #    body_parts.append(x.text)
        # return '<p>' + '</p><p>'.join(body_parts) + '</br></p>'

        return str(contents)
    # end def
# end class
