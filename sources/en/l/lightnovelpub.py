# -*- coding: utf-8 -*-
import logging
import re

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = '%s/search?title=%s'
chapter_list_url = '%s/chapters/page-%d'


class LightNovelOnline(Crawler):
    base_url = [
        'https://www.lightnovelpub.com/',
        'https://www.lightnovelworld.com/',
    ]

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(novel_search_url % (self.home_url, query))

        results = []
        for a in soup.select('.novel-list .novel-item a'):
            assert isinstance(a, Tag)
            possible_info = a.select_one('.novel-stats')
            info = possible_info.text.strip() if isinstance(possible_info, Tag) else None
            results.append({
                'title': str(a['title']).strip(),
                'url': self.absolute_url(a['href']),
                'info': info,
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        #self.novel_url = self.home_url + re.findall('/(novel/[^/]+)/', self.novel_url)[0]
        
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.novel-info .novel-title')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_image = soup.select_one('.glass-background img')
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        possible_author = soup.select_one('.author a[href*="/author/"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author['title']
        logger.info('Novel author: %s', self.novel_author)

        logger.info('Getting chapters...')
        soup = self.get_soup(chapter_list_url % (self.novel_url, 1))
        try:
            last_page = soup.select_one('.PagedList-skipToLast a')
            if not last_page:
                paginations = soup.select('.pagination li a[href*="/chapters/page"]')
                last_page = paginations[-2] if len(paginations) > 1 else paginations[0]
            assert isinstance(last_page, Tag)
            page_count = int(re.findall(r'/page-(\d+)', str(last_page['href']))[0])
        except Exception as err:
            logger.debug('Failed to parse page count. Error: %s', err)
            page_count = 0
        logger.info('Total pages: %d', page_count)

        futures = [
            self.executor.submit(self.get_soup, chapter_list_url % (self.novel_url, p))
            for p in range(2, page_count + 1)
        ]
        page_soups = [soup] + [f.result() for f in futures]

        for soup in page_soups:
            vol_id = len(self.volumes) + 1
            self.volumes.append({'id': vol_id})
            for a in soup.select('ul.chapter-list li a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a['title'],
                    'url': self.absolute_url(a['href']),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('#chapter-container')
        self.bad_css += ['.adsbox', 'p[class]', '.ad', 'p:nth-child(1) > strong']
        return self.extract_contents(body)
    # end def
# end class
