# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = 'https://www.tapread.com/book/contents?bookId=%s'
chapter_url = 'https://www.tapread.com/book/chapter?bookId=%s&chapterId=%s'


class TapreadCrawler(Crawler):
    base_url = 'https://www.tapread.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.book-name').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('img.bg-img, img.cover-img, .book-img img')['src'])
        except Exception:
            pass
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        try:
            possible_authors = []
            for div in soup.select('.author, .translator'):
                possible_authors.append(
                    ': '.join([x.strip() for x in div.text.split(':')]))
            # end for
            self.novel_author = ', '.join(possible_authors)
        except Exception:
            pass
        # end try
        logger.info(self.novel_author)

        path = urlparse(self.novel_url).path
        book_id = path.split('/')[3]
        data = self.get_json(chapter_list_url % book_id)

        volumes = set()
        for chap in data['result']['chapterList']:
            chap_id = chap['chapterNo']
            vol_id = (chap_id - 1) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': chap['chapterName'],
                'url': chapter_url % (chap['bookId'], chap['chapterId']),
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        data = self.get_json(chapter['url'])
        return data['result']['content']
    # end def
# end class
