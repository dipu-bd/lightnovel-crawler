#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger('QIDIAN_COM')


class QidianComCrawler(Crawler):
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

        self.novel_cover = self.absolute_url(
            soup.select_one('#bookImg img')['src'])
        self.novel_url = '/'.join(self.novel_url.split('/')[:-1])
        logger.info('Novel cover: %s', self.novel_cover)

        for volume in soup.select('.volume-wrap .volume'):
            vol_title = volume.select_one('h3')
            for tag in vol_title.select('a.subscri, span.free, em.count'):
                tag.decompose()
            # end for
            self.volumes.append({
                'id': len(self.volumes) + 1,
                'title': vol_title.text.strip(),
                'title_lock': True,
            })
            for li in volume.select('li'):
                a = li.select_one('a')
                self.chapters.append({
                    'id': int(li['data-rid']),
                    'volume': len(self.volumes),
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })
            # end for
        # end for

        logger.info('%d volumes and %d chapters found',
                    len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        chapter['body_lock'] = True
        chapter['title_lock'] = True
        chapter['title'] = soup.select_one('h3.j_chapterName').text.strip()
        return soup.select_one('div.j_readContent').extract()
    # end def
# end class
