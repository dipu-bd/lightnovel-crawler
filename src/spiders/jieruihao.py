#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [Jieruihao](https://www.jieruihao.cn).
"""
import logging

from ..utils.crawler import Crawler

logger = logging.getLogger('JIE_RUI_HAO')


class JieruihaoCrawler(Crawler):
    def initialize(self):
        self.home_url = 'https://www.jieruihao.cn'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        raw_title = soup.select_one('h1.page-title').text
        self.novel_title = raw_title.strip().replace('Category: ', '')
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = ""
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = None
        logger.info('Novel cover: %s', self.novel_cover)

        chapters = soup.select_one('div.content-area').select('ul li a')

        for x in chapters:
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id//100 + 1
                vol_title = 'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.select('div.entry-content p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
