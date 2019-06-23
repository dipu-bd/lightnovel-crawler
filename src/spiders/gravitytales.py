#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger('GRAVITY_TALES')

cover_image_url = 'https://cdn.gravitytales.com/images/covers/%s.jpg'
chapter_list_url = 'http://gravitytales.com/novel/%s/chapters'


class GravityTalesCrawler(Crawler):
    def read_novel_info(self):
        logger.debug('Visiting %s' % self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_id = self.novel_url.strip('/').split('/')[-1]
        logger.info('Novel ID: %s' % self.novel_id)

        self.novel_title = ' '.join([
            str(x) for x in
            soup.select_one('.main-content h3').contents
            if not x.name
        ]).strip()
        logger.info('Novel title: %s' % self.novel_title)

        self.novel_cover = cover_image_url % self.novel_id
        logger.info('Novel cover: %s' % self.novel_cover)

        self.novel_author = 'Translator: ' + \
            soup.select_one('.main-content h4').text
        logger.info(self.novel_author)

        self.get_chapters_list()
    # end def

    def get_chapters_list(self):
        url = chapter_list_url % self.novel_id
        logger.info('Visiting %s' % url)
        soup = self.get_soup(url)

        volumes = set([])
        for a in soup.select('table td a'):
            ch_id = len(self.chapters) + 1
            vol_id = 1 + (ch_id - 1) // 100
            volumes.add(vol_id)
            self.chapters.append({
                'id': ch_id,
                'volume': vol_id,
                'url': a['href'],
                'title': a.text.strip()
            })
        # end for

        self.volumes = [
            {'id': x, 'title': ''}
            for x in volumes
        ]

        logger.debug(self.chapters)
        logger.debug(self.volumes)
        logger.debug('%d chapters and %d volumes found',
                     len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s' % chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('#chapterContent')
        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
