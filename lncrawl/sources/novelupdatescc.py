# -*- coding: utf-8 -*-
import json
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.novelupdates.cc/search/%s/1'


class NovelUpdatesCC(Crawler):
    base_url = [
        'https://www.novelupdates.cc/',
    ]

    # FIXME: Can't seem to get search to work.
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('li.list-item'):
    #         a = tab.select_one('a.book-name')
    #         latest = "N/A"
    #         votes = tab.select_one('.star-suite span.score').text
    #         results.append({
    #             'title': a.text.strip(),
    #             'url': self.absolute_url(a['href']),
    #             'info': '%s | Rating: %s' % (latest, votes),
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('div.book-name').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            'div.author span.name').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.book-img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        chapters = soup.select('ul.chapter-list a')

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
                'title': a.select_one('p.chapter-name').text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.info('%d chapters and %d volumes found',
                    len(self.chapters), len(self.volumes))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        chapter['title'] = soup.select_one('h1.chapter-title').text.strip()

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]
        body_parts = soup.select_one('div.chapter-entity')
        for br in body_parts.select('br'):
            br.decompose()
        body = self.extract_contents(body_parts)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class