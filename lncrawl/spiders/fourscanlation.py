#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('4SCANLATION')


class FourScanlationCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = "Translated by 4scanlation"
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.page-header-image.grid-container.grid-parent img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('p a')[1:-2]

        for a in chapters:
            if a.text.strip().lower().startswith('prolog') or a.text.strip().lower().startswith('chapter'):
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
            # end if
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.entry-content')

        for d in contents.findAll('div'):
            d.decompose()
        # end for

        chapter['title'] = soup.select_one('h1.entry-title').text

        logger.debug(chapter['title'])
        
        return contents.prettify()
    # end def
# end class
