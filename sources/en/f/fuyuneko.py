# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Fuyuneko(Crawler):
    base_url = 'https://www.fuyuneko.org/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('title').text
        self.novel_title = self.novel_title.split('—')[0].strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('figure.sqs-block-image-figure img')['src'])
        #logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by Fuyu Neko's"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'section#page p [href*="fuyuneko.org/"]')

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

        # Removes "Previous | Table of Contents | Next" from bottom of chapters.
        for content in body_parts.select("p"):
            for bad in ["Previous", "Table of Contents", "Next", "  |  "]:
                if bad in content.text:
                    content.extract()
 
        return self.extract_contents(body_parts) 
    # end def
# end class
