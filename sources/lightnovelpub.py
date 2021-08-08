# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = '%s/search?title=%s'
chapter_list_url = '%s/novel/%s?tab=chapters&page=%d&chorder=asc'


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
            results.append({
                'title': a['title'].strip(),
                'url': self.absolute_url(a['href']),
                'info': a.select_one('.novel-stats').text.strip(),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        self.novel_url = '%s%s' % (self.home_url, urlparse(self.novel_url).path)

        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.novel-info .novel-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_id = urlparse(self.novel_url).path.split('/')[-1]
        logger.info('Novel id: %s', self.novel_id)

        self.verificationToken = soup.select_one(
            'input[name="__RequestVerificationToken"]')['value']
        logger.info('Verification token: %s', self.verificationToken)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('.novel-header .cover img')['data-src'])
        except Exception as err:
            logger.debug('Failed to parse novel cover. Error: %s', err)
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        try:
            self.novel_author = soup.select_one('.author a[href*="/author/"]')['title']
        except Exception as err:
            logger.debug('Failed to parse novel author. Error: %s', err)
        # end try
        logger.info('Novel author: %s', self.novel_author)

        try:
            last_page = soup.select_one('.PagedList-skipToLast a')
            if not last_page:
                last_page = soup.select('.pagination li a:not([rel="next"])')[-1]
            page_count = int(re.findall(r'page=(\d+)', last_page['href'])[0])
        except Exception as err:
            logger.debug('Failed to parse page count. Error: %s', err)
            page_count = 0
        logger.info('Total pages: %d', page_count)

        logger.info('Getting chapters...')
        futures = [
            self.executor.submit(self.extract_chapter_list, i + 1)
            for i in range(page_count + 1)
        ]

        volumes = set([])
        for f in futures:
            for chap in f.result():
                chap['id'] = len(self.chapters) + 1
                chap['volume'] = len(self.chapters) // 100 + 1
                self.chapters.append(chap)
                volumes.add(chap['volume'])
            # end for
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def extract_chapter_list(self, page):
        response = self.submit_form(
            chapter_list_url % (self.home_url, self.novel_id, page),
            data='X-Requested-With=XMLHttpRequest',
            headers={
                'requestverificationtoken': self.verificationToken,
                'origin': self.home_url,
            },
        )
        soup = self.make_soup(response)

        temp_list = []
        for li in soup.select('.chapter-list li'):
            a = li.select_one('a')
            temp_list.append({
                'title': a['title'],
                'url': self.absolute_url(a['href']),
            })
        # end for
        return temp_list
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        body = soup.select_one('.chapter-content')
        for ads in body.select('div[class*="ad"], script, ins, p[class]'):
            ads.extract()
        # end for
        return self.extract_contents(body)
    # end def
# end class
