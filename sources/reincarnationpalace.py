# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler
from bs4 import Comment

logger = logging.getLogger(__name__)

class ReincarnationPalace(Crawler):
    base_url = 'https://reincarnationpalace.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'meta[property="og:title"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.elementor-image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('div.elementor-widget-container p')[6].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # FIXME: I've found one chapters it can't download, it has a ` or %60 at end of url which seems to make crawler ignore it for some reason. If anyone know how to fix please do so.
        chapters = soup.select('h4 a[href*="reincarnationpalace"]')

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

        body_parts = soup.select_one('.entry-content')

        # remove social media buttons
        for share in body_parts.select('div.sharedaddy'):
            share.extract()

        # remove urls
        self.bad_tags += ['a']

        # remove comments
        for comment in soup.findAll(text=lambda text:isinstance(text, Comment)):
            comment.extract()

        self.clean_contents(body_parts)

        # remove double spacing
        

        return self.extract_contents(body_parts)
    # end def
# end class