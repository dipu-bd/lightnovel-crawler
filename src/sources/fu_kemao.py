# -*- coding: utf-8 -*-
import logging
import re
from base64 import decodestring as b64decode
from concurrent import futures
from urllib.parse import quote_plus

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = b64decode(
    "aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8/cG9zdF90eXBlPW5vdmVsJnM9".encode()).decode()


class Fu_kCom_ademao(Crawler):
    base_url = b64decode("aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8=".encode()).decode()

    def search_novel(self, query):
        url = novel_search_url + quote_plus(query)
        # logger.debug('Visiting: ' + url)
        soup = self.get_soup(url)

        results = []
        for a in soup.select('#novel a'):
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        # logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h3.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('#thumbnail img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one('#Publisher a')['href']
        logger.info('Novel author: %s', self.novel_author)

        page_count = 1
        pagination = soup.select_one('.pagination')
        if pagination:
            next_tag = pagination.select_one('.next')
            page_count = int(next_tag.findPrevious('a').text)
        # end if
        logger.info('Total chapter pages: %d' % page_count)

        def parse_chapter_list(soup):
            temp_list = []
            for a in soup.select('.chapter-list td a'):
                temp_list.append({
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })
            # end for
            return temp_list
        # end def

        def download_chapter_list(page):
            url = self.novel_url.split('?')[0].strip('/') + '/page/%d' % page
            # logger.debug('Visiting for chapter list: ' + url)
            soup = self.get_soup(url)
            return parse_chapter_list(soup)
        # end def

        logger.info('Getting chapters...')
        temp_chapters = dict()
        futures_to_check = dict()
        for page in range(1, page_count + 1):
            if page == 1:
                future = self.executor.submit(
                    parse_chapter_list,
                    soup
                )
            else:
                future = self.executor.submit(
                    download_chapter_list,
                    page
                )
            # end if
            futures_to_check[page] = future
        # end for
        for page, future in futures_to_check.items():
            temp_chapters[page] = future.result()
        # end for

        logger.info('Building sorted chapter list...')
        for page in reversed(sorted(temp_chapters.keys())):
            for chap in reversed(temp_chapters[page]):
                chap['volume'] = page
                chap['id'] = len(self.chapters) + 1
                self.chapters.append(chap)
            # end for
        # end for
        self.volumes = [
            {'id': i + 1} for i in range(page_count)
        ]
    # end def

    def download_chapter_body(self, chapter):
        # logger.info('Downloading ' + chapter['url'])
        soup = self.get_soup(chapter['url'])
        # logger.debug(soup.title.string)

        contents = soup.find("div", attrs={"readability": True})
        if not contents:
            contents = soup.find("article")
        # end if

        for tag in soup.findAll(attrs={"class": True}):
            tag.extract()
        # end for

        return str(contents)
    # end def
# end class
