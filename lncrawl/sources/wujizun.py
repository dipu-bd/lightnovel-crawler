# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.cleaner import cleanup_text
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

class Wujizun(Crawler):
    base_url = 'https://wujizun.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            'meta[property="og:title"]')['content']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = soup.select_one(
            'meta[property="og:image"]')['content']
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by Wujizun"
        logger.info('Novel author: %s', self.novel_author)

        # Removes none TOC links from bottom of page.
        toc_parts = soup.select_one('div.entry-content')
        for notoc in toc_parts.select('.sharedaddy, .ezoic-adpicker-ad, .ezoic-ad-adaptive, .ezoic-ad'):
            notoc.decompose()

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content p a[href*="wujizun.com/2"]')

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

        logger.debug(soup.title.string)

        body_parts = soup.select_one('div.entry-content')

        # Removes "Share this" text and buttons from bottom of chapters. Also other junk on page.
        for share in body_parts.select('iframe, .sharedaddy, .jp-relatedposts, .inline-ad-slot, .code-block, script, hr, .adsbygoogle, .ezoic-adpicker-ad, .ezoic-ad-adaptive, .ezoic-ad, .cb_p6_patreon_button'):
            share.decompose()

        # Remoeves bad text from chapters.
        for content in body_parts.select("p"):
            for bad in ["Previous Chapter", "Table of Contents", "Next Chapter"]:
                if bad in content.text:
                    content.decompose()

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