#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger('MEIONOVEL')


class MeionovelCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one('h1.entry-title').text.strip()
        self.novel_title = ('%s Bahasa Indonesia by Meionovel' % title)
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.lightnovel-box .lightnovel-thumb img')['data-lazy-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by meionovel.com"
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('div.lightnovel-episode ul li a._link')

        chapters.reverse()

        for a in chapters:
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
                'url':  self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('div.entry-content')

        body = self.extract_contents(body_parts)

        signature = '</br>Kunjungi web kami yaitu <a href="https://meionovel.id">meionovel.id</a>'

        body.append(signature)

        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
