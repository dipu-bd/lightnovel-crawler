# -*- coding: utf-8 -*-
import json
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger('VIS_TRANS')

class VisTranslations(Crawler):
    base_url = 'https://vistranslations.wordpress.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        # NOTE: Could not get cover kept coming back with error.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('div.entry-content div.wp-block-media-text img')['data-orig-file'])
        # logger.info('Novel cover: %s', self.novel_cover)

        # Could not get author name from site, just replaced with translators name.
        self.novel_author = "by VisTranslations"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # FIXME: Sometimes grabs social media link at bottom of page, No idea how to exclude links.
        chapters = soup.select('table td [href*="vistranslations.wordpress.com"]')

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

        body = []
        contents = soup.select('div.entry-content p')
        for p in contents:
            para = ' '.join(self.extract_contents(p))
            if len(para):
                body.append(para)
            # end if
        # end for

        return '<p>%s</p>' % '</p><p>'.join(body)
    # end def
# end class