#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for http://fullnovel.live/
"""
import logging
from ..utils.crawler import Crawler

logger = logging.getLogger('FULLNOVEL_LIVE')

NOVEL_SEARCH = 'http://fullnovel.live/search/%s'


class FullnovelLiveCrawler(Crawler):
    def search_novel(self, query):
        '''Gets a list of (title, url) matching the given query'''
        results = []
        soup = self.get_soup(NOVEL_SEARCH % query)
        for grid in soup.select('.grid .v-grid'):
            a = grid.select_one('h4 a')
            info = grid.select_one('.info-line a').text
            results.append({
                'title': (a['title'] or a.text).strip(),
                'url': self.absolute_url(a['href']),
                'info': info
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one('.info h1.title a').text.strip()
        self.novel_cover = self.absolute_url(
            soup.select_one('.info .image img')['src'])

        chapters = soup.select('.scroll-eps a')
        chapters.reverse()

        for x in chapters:
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
                'url': self.absolute_url(x['href']),
                'title': x.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.page .divContent')
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p'
    # end def
# end class
