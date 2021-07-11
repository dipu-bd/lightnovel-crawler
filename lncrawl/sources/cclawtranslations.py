# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.cleaner import cleanup_text
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

class CclawTranslations(Crawler):
    base_url = 'https://cclawtranslations.home.blog/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one(
            'meta[property="og:title"]')['content']
        self.novel_title = title.rsplit(' ', 1)[0].strip()
        logger.debug('Novel title = %s', self.novel_title)

        self.novel_cover = soup.select_one(
            'meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select_one(
            'meta[property="og:site_name"]')['content']
        logger.info("%s", self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one('div.entry-content')
        for notoc in toc_parts.select('.sharedaddy, .inline-ad-slot, .code-block, script, hr, .adsbygoogle'):
            notoc.decompose()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content a[href*="cclawtranslations.home.blog/2"]')

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

    @cleanup_text
    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('div.entry-content')

        # Removes "Share this" text and buttons from bottom of chapters. Also other junk on page.
        for share in body_parts.select('.sharedaddy, .inline-ad-slot, .code-block, script, hr, .adsbygoogle'):
            share.decompose()

        # Fixes images, so they can be downloaded.
        all_imgs = soup.find_all('img')
        for img in all_imgs:
            if img.has_attr('data-orig-file'):
                src_url = img['src']
                parent = img.parent
                img.decompose()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        return str(body_parts)
    # end def
# end class