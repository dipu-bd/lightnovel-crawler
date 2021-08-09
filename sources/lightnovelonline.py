# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://light-novel.online/search.ajax?query=%s'
novel_page_url = 'https://light-novel.online/%s?page=%d'


class LightNovelOnline(Crawler):
    base_url = 'https://light-novel.online/'

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)
        results = []

        if soup.get_text(strip=True) == 'Sorry! No novel founded!':
            return results
        # end if
        for tr in soup.select('tr'):
            a = tr.select('td a')
            results.append({
                'title': a[0].text.strip(),
                'url': self.absolute_url(a[0]['href']),
                'info': a[1].text.strip(),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_id = urlparse(self.novel_url).path.split('/')[-1]
        logger.info("Novel Id: %s", self.novel_id)

        self.novel_title = soup.select_one(
            '.series-details .series-name a').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.series-cover .content')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # self.novel_author
        # logger.info('Novel author: %s', self.novel_author)

        page_count = 1
        try:
            last_page = soup.select('ul.pagingnation li a')[-1]['title']
            page_count = int(last_page.split(' ')[-1])
        except Exception as _:
            logger.exception('Failed to get page-count: %s', self.novel_url)
        # end try
        logger.info('Total pages: %d', page_count)

        logger.info('Getting chapters...')
        futures_to_check = {
            self.executor.submit(
                self.extract_chapter_list,
                i + 1,
            ): str(i)
            for i in range(page_count)
        }
        temp_chapters = dict()
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            temp_chapters[page] = future.result()
        # end for

        logger.info('Building sorted chapter list...')
        for page in reversed(sorted(temp_chapters.keys())):
            for chap in reversed(temp_chapters[page]):
                chap['id'] = len(self.chapters) + 1
                chap['volume'] = len(self.chapters) // 100 + 1
                self.chapters.append(chap)
            # end for
        # end for

        self.volumes = [{'id': i + 1}
                        for i in range(1 + len(self.chapters) // 100)]
    # end def

    def extract_chapter_list(self, page):
        url = novel_page_url % (self.novel_id, page)
        logger.debug('Getting chapter list: %s', url)
        soup = self.get_soup(url)

        temp_list = []
        for a in soup.select('ul.list-chapters .chapter-name a'):
            temp_list.append({
                'title': a.text.strip(),
                'url': self.absolute_url('/' + a['href'].strip('/')),
            })
        # end for
        return temp_list
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('#chapter-content')
        return str(body)
        # return ''.join([str(p) for p in body if p.text.strip()])
    # end def
# end class
