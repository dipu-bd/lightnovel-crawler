# -*- coding: utf-8 -*-
import json
import logging
import re

from ..utils.crawler import Crawler
from bs4 import Comment

logger = logging.getLogger(__name__)

class hui3rCrawler(Crawler):
    base_url = 'https://hui3r.wordpress.com/'

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('.single-entry-content h3 a').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        # NOTE: Having trouble grabbing cover without error message.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('.single-entry-content p img')['src'])
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "by hui3r"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # NOTE: Addd /2 to end of url, so it only grabs chapters instead of social media links as well.
        chapters = soup.select('.single-entry-content ul li a[href*="hui3r.wordpress.com/2"]')

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

        body_parts = soup.select_one('.single-entry-content')

        # Removes "Share this" text and buttons from bottom of chapters.
        for share in body_parts.select('div.sharedaddy'):
            share.decompose()

        # Removes footer info and categories.
        for footer in body_parts.select('footer.entry-meta'):
            footer.decompose()

        # Removes watermark/hidden text
        for hidden in body_parts.findAll('span', {'style': 'color:#ffffff;'}):
            hidden.decompose()

        # remove comments
        for comment in soup.findAll(text=lambda text:isinstance(text, Comment)):
            comment.extract()

        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class