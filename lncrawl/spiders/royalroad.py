#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [novelonlinefree.info](https://novelonlinefree.info/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from ..utils.crawler import Crawler

logger = logging.getLogger('ROYALROAD')
search_url = 'https://www.royalroad.com/fictions/search?keyword=%s'


class RoyalRoadCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        response = self.get_response(search_url % query)
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for a in soup.select('h2.margin-bottom-10 a'):
            results.append((
                a.text.strip(),
                self.absolute_url(a['href']),
            ))
        # end for

        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        response = self.get_response(self.novel_url)
        soup = BeautifulSoup(response.content, 'lxml')

        self.novel_title = soup.find("h1", {"property": "name"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find("img", {"class": "img-offset thumbnail inline-block"})['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.find("h4", {"property": "author"}).text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find('tbody').findAll('a', href=True)

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

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.content, 'lxml')

        logger.debug(soup.title.string)

        if 'Chapter' in soup.select_one('h2').text:
            chapter['title'] = soup.select_one('h2').text
        else:
            chapter['title'] = chapter['title']
        # end if

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.find("div", {"class": "chapter-content"})
        #body = self.extract_contents(contents)
        #return '<p>' + '</p><p>'.join(body) + '</p>'
        return contents.prettify()
    # end def
# end class
