# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = 'https://book.qidian.com/ajax/book/category?_csrfToken=%s&bookId=%s'
chapter_details_url = 'https://read.qidian.com/chapter/%s'


class QidianComCrawler(Crawler):
    base_url = [
        'https://book.qidian.com/',
        # 'https://www.qidian.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.qidian.com/'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.book-info h1 em').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('.book-info h1 a.writer').text
        logger.info('Novel author: %s', self.novel_author)

        book_img = soup.select_one('#bookImg')
        self.novel_cover = self.absolute_url(book_img.find('img')['src'])
        self.novel_cover = '/'.join(self.novel_cover.split('/')[:-1])
        logger.info('Novel cover: %s', self.novel_cover)

        self.book_id = book_img['data-bid']
        logger.debug('Book Id: %s', self.book_id)

        self.csrf = self.cookies['_csrfToken']
        logger.debug('CSRF Token: %s', self.csrf)

        volume_url = chapter_list_url % (self.csrf, self.book_id)
        logger.debug('Visiting %s', volume_url)
        data = self.get_json(volume_url)

        for volume in data['data']['vs']:
            vol_id = len(self.volumes) + 1
            self.volumes.append({
                'id': vol_id,
                'title': volume['vN'],
            })
            for chapter in volume['cs']:
                ch_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': ch_id,
                    'volume': vol_id,
                    'title': chapter['cN'],
                    'url': chapter_details_url % chapter['cU'],
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        chapter['title'] = soup.select_one('h3.j_chapterName').text.strip()
        return soup.select_one('div.j_readContent').extract()
    # end def
# end class
