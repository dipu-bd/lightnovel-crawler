#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [readlightnovel.org](https://www.readlightnovel.org/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('READLIGHTNOVEL')
search_url = 'https://www.readlightnovel.org/search/autocomplete'


class ReadLightNovelCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.block-title h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('img', {'alt': self.novel_title})['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author_link = soup.select_one("a[href*=author]")
        if author_link:
            self.novel_author = author_link.text.strip().title()
        # end if
        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('.chapters .chapter-chs li a'):
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

        div = soup.select_one('.chapter-content3 .desc')
        hidden = div.select_one('#growfoodsmart')
        if hidden:
            hidden.decompose()
        # end if

        body = self.extract_contents(div)
        if re.search(r'c?hapter .?\d+', body[0], re.IGNORECASE):
            chapter['title'] = body[0].replace(
                '<strong>', '').replace('</strong>', '').strip()
            chapter['title'] = ('C' if chapter['title'].startswith(
                'hapter') else '') + chapter['title']
            body = body[1:]
        # end if

        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
