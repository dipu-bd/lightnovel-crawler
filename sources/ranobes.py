# -*- coding: utf-8 -*-
import logging
from concurrent.futures import ThreadPoolExecutor

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RanobeLibCrawler(Crawler):
    base_url = [
        'http://ranobes.net/',
        'https://ranobes.net/',
    ]

    def initialize(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=1)
    # end def

    def read_novel_info(self):
        logger.info('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        main_page_link = soup.select_one('#mainside a[href*="/novels/"]')
        if main_page_link:
            self.novel_url = self.absolute_url(main_page_link['href'])
            soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title['content']
        logger.info('Novel title: %s', self.novel_title)

        possible_cover = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_cover, Tag):
            self.novel_cover = self.absolute_url(possible_cover['content'])
        logger.info('Novel cover: %s', self.novel_cover)

        author_link = soup.select_one('.tag_list[itemprop="author"] a')
        if author_link:
            self.novel_author = author_link.text.strip().title()
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapter_list_link = soup.select_one('#fs-chapters a[title="Go to table of contents"]')
        assert isinstance(chapter_list_link, Tag)
        chapter_list_link = self.absolute_url(chapter_list_link['href'])

        soup = self.get_soup(chapter_list_link)
        last_page = int(soup.select('.navigation .pages a')[-1].text)

        futures = []
        page_soups = [soup]
        for i in range(2, last_page + 1):
            chapter_page_url = chapter_list_link.strip('/') + ('/page/%d' % i)
            f = self.executor.submit(self.get_soup, chapter_page_url)
            futures.append(f)
        page_soups += [f.result() for f in futures]

        volumes = set([])
        for soup in reversed(page_soups):
            for a in reversed(soup.select('#dle-content .cat_line a')):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                volumes.add(vol_id)
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a['title'],
                    'url': self.absolute_url(a['href']),
                })

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        article = soup.select_one('.text[itemprop="description"]')

        self.bad_css += [
            '.free-support',
            'div[id^="adfox_"]'
        ]
        self.clean_contents(article)

        return str(article)
    # end def
# end class
