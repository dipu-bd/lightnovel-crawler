# -*- coding: utf-8 -*-
import json
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger('JUSTATRANS')

class JustATranslatorTranslations(Crawler):
    base_url = 'https://justatranslatortranslations.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.entry-content p img')['data-orig-file'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('div.entry-content p')[3].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content p [href*="justatranslatortranslations.com/"]')

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

        logger.debug(soup.title.string)

        body_parts = soup.select_one('div.entry-content')

        # Removes "Share this" text and buttons from bottom of chapters.
        for share in body_parts.select('div.sharedaddy'):
            share.decompose()

        # Removes footnote numbers.
        for footnote in body_parts.select('sup'):
            footnote.decompose()

        # Remoeves Nav Button from top and bottom of chapters.
        for content in body_parts.select("p"):
            for bad in ["[Previous]", "[Next]", "[Table of Contents]"]:
                if bad in content.text:
                    content.decompose()

        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class