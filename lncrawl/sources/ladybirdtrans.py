# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class lazybirdtranslations(Crawler):
    base_url = 'https://lazybirdtranslations.wordpress.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_cover = soup.select_one(
            'meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_title = soup.select_one(
            'meta[property="og:title"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        authors = []
        for a in soup.select('figcaption'):
                authors.append(a.text.strip())
            # end if
        # end for
        self.novel_author = ', '.join(authors)
        logger.info('Novel author: %s', self.novel_author)

        # Stops external links being selected as chapters
        chapters = soup.select('.wp-block-table tr td a[href*="lazybirdtranslations.wordpress.com/2"]')

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

        # Adds proper chapter ttile, only problem is some are in 2 parts so there named the same.
        if 'Chapter' in soup.select_one('h2').text:
            chapter['title'] = soup.select_one('h2').text
        else:
            chapter['title'] = chapter['title']
        # end if

        body_parts = soup.select_one('div.entry-content')

        for content in body_parts.select("p"):
            for bad in ["[Index]", "[Previous]", "[Next]"]:
                if bad in content.text:
                    content.extract()

        for bad in body_parts.select('br, .entry-meta, .inline-ad-slot, .has-text-align-center, #jp-post-flair, .entry-footer'):
            bad.extract()

        return self.extract_contents(body_parts)
    # end def
# end class