#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('VOLARE_NOVELS')


class VolareNovelsCrawler(Crawler):
    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(
            '#content-container h3.title').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_author = soup.select('#content-container .p-tb-10-rl-30 p')[1].text.strip()
        except Exception:
            pass  # not so important to raise errors
        # end try
        logger.info('Novel author: %s', self.novel_author)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('#content-container .md-d-table img')['src'])
        except Exception:
            pass  # not so important to raise errors
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapter_urls = set([])
        for div in soup.select('#TableOfContents #accordion .panel'):
            vol_id = len(self.volumes) + 1
            vol_title = div.select_one('h4.panel-title .title a').text.strip()

            try:
                vol_id = int(div.select('h4.panel-title span')[0].text.strip())
            except Exception:
                pass
            # end try

            self.volumes.append({
                'id': vol_id,
                'title': vol_title,
            })
            for a in div.select('.list-chapters li a'):
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                })
                chapter_urls.add(a['href'])
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting: %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('.panel .panel-body .fr-view')
        # self.clean_contents(content)
        return str(content)
    # end def
# end class
