# -*- coding: utf-8 -*-
import json
import logging
import re
import ast
import requests
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = 'https://jpmtl.com/books/%s'
chapters_url = 'https://jpmtl.com/v2/chapter/%s/list?state=published&structured=true&direction=false'


class JpmtlCrawler(Crawler):
    machine_translation = True
    base_url = 'https://jpmtl.com/'

    def initialize(self):
        self.home_url = 'https://jpmtl.com'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        self.novel_id = self.novel_url.split('/')[-1]
        logger.info('Novel Id: %s', self.novel_id)

        self.novel_url = book_url % self.novel_id
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'h1.book-sidebar__title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('.book-sidebar__img img')['src'])
            logger.info('Novel cover: %s', self.novel_cover)
        except Exception:
            logger.debug('Failed to get cover: %s', self.novel_url)
        # end try

        self.novel_author = soup.select_one(
            '.book-sidebar__author .book-sidebar__info').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        toc_url = chapters_url % self.novel_id

        toc = self.get_json(toc_url)
        for volume in toc:
            self.volumes.append({
                'id': volume['volume'],
                'title': volume['volume_title'],
            })
            for chapter in volume['chapters']:
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': volume['volume'],
                    'url':  self.absolute_url(self.novel_url+'/'+str(chapter['id'])),
                    'title': chapter['title'] or ('Chapter %d' % chap_id),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select('.chapter-content__content p')

        body = [str(p) for p in contents if p.text.strip()]

        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
