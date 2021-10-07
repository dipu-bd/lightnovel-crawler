# -*- coding: utf-8 -*-
import logging
from concurrent.futures import Future
from typing import List, Optional
from urllib.parse import quote, urlencode

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://truyentr.info/?s=%s'


class TruenFull(Crawler):
    machine_translation = True
    base_url = [
        'https://truyenfull.vn/',
        'https://truyentr.info/'
    ]

    @staticmethod
    def __select_value(tag: Tag, css: str, attr: Optional[str]=None):
        possible_item = tag.select_one(css)
        if not isinstance(possible_item, Tag):
            return ''
        # end if
        if attr:
            return (getattr(possible_item, 'attrs') or {}).get(attr)
        else:
            return (getattr(possible_item, 'text') or '').strip()
        # end if
    # end def


    def search_novel(self, query):
        soup = self.get_soup(search_url % quote(query))

        results = []
        for div in soup.select('.cate-list-books .list-item'):
            a = div.select_one('.truyen-title a')
            if not isinstance(a, Tag):
                continue

            status_info = self.__select_value(div, '.status-info')
            author = self.__select_value(div, '.author')
            latest = self.__select_value(div, '.item-col.text-info a')
            info = [x for x in [latest, author, status_info] if x]

            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': ' | '.join(info),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('h3.title, h1.title')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.__select_value(soup, '.book-thumb img, .books .book img', 'src')
        logger.info('Novel cover: %s', self.novel_cover)

        authors = soup.select('.info a[itemprop="author"]')
        self.novel_author = ', '.join([x.text for x in authors if isinstance(x, Tag)])
        logger.info('Novel author: %s', self.novel_author)

        if '//truyentr.info/' in self.novel_url:
           self.parse_truyentr_chapters(soup)
        else:
            self.parse_truyenfull_chapters(soup)
        # end if
    # end def

    def parse_truyentr_chapters(self, soup: Tag):
        total_page = 1
        pagination = soup.select('.pagination li a')
        if len(pagination):
            last_page_url = str(pagination[-1]['href'])
            logger.info('Last page url: %s', last_page_url)
            if '?trang=' in last_page_url:
                total_page = int(last_page_url.split('trang=')[1])
            # end if
        # end if
        logger.info('Total page count = %d', total_page)

        futures: List[Future] = []
        for page in range(1, total_page):
            url = self.novel_url + f'?trang={page + 1}'
            logger.info('Visiting %s', url)
            f = self.executor.submit(self.get_soup, url)
            futures.append(f)
        # end for

        self.parse_all_links(soup.select('.list-chapters a'))

        for f in futures:
            soup = f.result()
            self.parse_all_links(soup.select('.list-chapters a'))
        # end for
    # end def

    def parse_truyenfull_chapters(self, soup: Tag):
        truyen_id = self.__select_value(soup, 'input#truyen-id', 'value')
        total_page = self.__select_value(soup, 'input#total-page', 'value')
        truyen_ascii = self.__select_value(soup, 'input#truyen-ascii', 'value')
        assert truyen_id, 'No truen novel id found'
        total_page = int(str(total_page))
        logger.info('Total page count: %d', total_page)

        futures: List[Future] = []
        for page in range(total_page):
            params = urlencode({
                'type': 'list_chapter',
                'tid': int(truyen_id),
                'tascii': truyen_ascii,
                'tname': self.novel_title,
                'page': page + 1,
                'totalp': total_page,
            })
            url = 'https://truyenfull.vn/ajax.php?' + params
            logger.info('Getting chapters: %s', url)
            f = self.executor.submit(self.get_json, url)
            futures.append(f)
        # end for

        for f in futures:
            data = f.result()
            soup = self.make_soup(data['chap_list'])
            self.parse_all_links(soup.select('.list-chapter a'))
        # end for
    # end def

    def parse_all_links(self, links: List[Tag]):
        for a in links:
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url': self.absolute_url(a['href']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('#chapter-c, .chapter-c')

        self.bad_css = [
            '.ads-content',
            '.ads-inpage-container',
            '.ads-responsive',
            '.ads-pc',
            '.ads-chapter-box',
            '.incontent-ad',
            '.ads-network',
            '.ads-desktop',
            '.ads-mobile',
            '.ads-holder',
            '.ads-taboola',
            '.ads-middle',
            '.adsbygoogle',
        ]
        return self.extract_contents(contents)
    # end def
# end class
