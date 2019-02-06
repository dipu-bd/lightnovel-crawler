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

logger = logging.getLogger('NOVEL_ONLINE_FREE')
search_url = 'https://novelonlinefree.info/search_novels/%s?q=%s'


class NovelOnlineFreeCrawler(Crawler):
    def search_novel(self, query):
        query1 = query.lower().replace(' ', '_')
        query2 = query.lower().replace(' ', '+')
        response = self.get_response(search_url % (query1,query2))
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for a in soup.select('.update_item h3 a'):
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

        self.novel_title = soup.select_one('h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find('img', {'class': 'attachment-large size-large wp-post-image'})['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for span in soup.find_all('span'):
            if span.text.startswith('Author(s): '):
                author = span.findNext('a').text
                author1 = span.findNext('a').findNext('a').text
        self.novel_author = author + ' (' + author1 + ')'
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find('div',{'class':'chapter-list'}).find_all('div', {'class':'row'})
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
                'url': self.absolute_url(x.find('a')['href']),
                'title': x.find('a')['title'] or ('Chapter %d' % chap_id),
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

        if 'Chapter' in soup.select_one('h1').text:
            chapter['title'] = soup.select_one('h1').text
        else:
            chapter['title'] = chapter['title']
        # end if

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.select_one('#vung_doc')
        body = self.extract_contents(contents)
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
