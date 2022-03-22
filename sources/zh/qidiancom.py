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
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.book-info h1 em')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text
        logger.info('Novel title: %s', self.novel_title)

        possible_author = soup.select_one('.book-info h1 a.writer')
        if possible_author:
            self.novel_author = possible_author.text
        logger.info('Novel author: %s', self.novel_author)

        book_img = soup.select_one('#bookImg img')
        assert book_img, 'No book image found'

        self.book_id = book_img['data-bid']
        logger.info('Book Id: %s', self.book_id)

        bool_img_src = '/'.join(str(book_img['src']).split('/')[:-1])
        self.novel_cover = self.absolute_url(bool_img_src)
        logger.info('Novel cover: %s', self.novel_cover)

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
        soup = self.get_soup(chapter['url'])

        possible_title = soup.select_one('h3.j_chapterName')
        if possible_title:
            chapter['title'] = possible_title.text.strip()
        # end if

        contents = soup.select_one('div.j_readContent')
        return self.cleaner.extract_contents(contents)
    # end def
# end class
