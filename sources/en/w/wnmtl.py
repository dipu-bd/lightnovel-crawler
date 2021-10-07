# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote, urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

SEARCH_URL = 'https://api.mystorywave.com/story-wave-backend/api/v1/content/books/search?keyWord=%s&pageNumber=1&pageSize=50'
BOOK_INFO_URL = 'https://api.mystorywave.com/story-wave-backend/api/v1/content/books/%s'
CHAPTER_LIST_URL = 'https://api.mystorywave.com/story-wave-backend/api/v1/content/chapters/page?sortDirection=ASC&bookId=%s&pageNumber=%d&pageSize=100'
CHAPTER_CONTENT_URL = 'https://api.mystorywave.com/story-wave-backend/api/v1/content/chapters/%d'


class WNMTLCrawler(Crawler):
    machine_translation = True

    base_url = [
        'https://www.wnmtl.org/',
        'https://wnmtl.org/',
        'http://www.wnmtl.org/',
        'http://wnmtl.org/',
    ]

    # NOTE: Disabled because it takes too long to responsd
    # def search_novel(self, query):
    #     url = SEARCH_URL % quote(query).lower()
    #     data = self.get_json(url)
    #     results = []
    #     for item in data['data']['list']:
    #         results.append({
    #             'title': item['title'],
    #             'url': 'https://wnmtl.org/book/' + item['id'],
    #             'info': 'Author: %s | %s | Last update: %s %s' % (
    #                 item['authorPseudonym'], item['genreName'], item['lastUpdateChapterOrder'], item['lastUpdateChapterTitle']),
    #         })
    #     # end for
    #     return results
    # # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug(self.home_url)
        self.scraper.headers['site-domain'] = urlparse(self.novel_url).hostname or ''

        self.novel_id = int(urlparse(self.novel_url).path.split('/')[2].split('-')[0])
        logger.info('Novel ID %d', self.novel_id)

        data = self.get_json(BOOK_INFO_URL % self.novel_id)
        logger.debug(data)

        self.novel_title = data['data']['title']
        self.novel_cover = data['data']['coverImgUrl']
        self.novel_author = data['data']['authorPseudonym']

        chapter_data = []
        data = self.get_json(CHAPTER_LIST_URL % (self.novel_id, 1))
        chapter_data += data['data']['list']

        futures = []
        for page in range(2, data['data']['totalPages'] + 1):
            url = CHAPTER_LIST_URL % (self.novel_id, page)
            futures.append(self.executor.submit(self.get_json, url))
        # end for

        for f in futures:
            data = f.result()
            chapter_data += data['data']['list']
        # end for

        for item in chapter_data:
            if item['paywallStatus'] != "free" or item['status'] != "published":
                continue
            # end if
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({'id': vol_id})
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': CHAPTER_CONTENT_URL % item['id'],
                'title': 'Chapter %d: %s' % (item['chapterOrder'], item['title']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        data = self.get_json(chapter['url'])
        contents = data['data']['content'].split('\n')
        return '\n'.join(['<p>' + x + '</p>' for x in contents])
    # end def
# end class
