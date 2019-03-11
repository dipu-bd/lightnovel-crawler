#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
from bs4 import BeautifulSoup
from ..utils.crawler import Crawler

logger = logging.getLogger('LITNET')
search_url = 'https://litnet.com/en/search?q=%s'

class LitnetCrawler(Crawler):

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        response = self.get_response(search_url % query)
        soup = BeautifulSoup(response.text, 'lxml')

        results = []
        for a in soup.select('div.l-container ul a'):
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

        img_src = soup.select_one('div.book-view-cover img')
        if img_src is None:
            img_src = soup.select_one('div.book-cover img')
        self.novel_cover = self.absolute_url(img_src['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select_one('div.book-view-info a.author')
        if author is None:
            author = soup.select_one('div.book-head-content a.book-autor')
        self.novel_author = author.text.strip()
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find('select', {'name': 'chapter'})
        if chapters is None:
            chapters = soup.select('div.collapsible-body a.collection-item')
        else:
            chapters = chapters.find_all('option')
            chapters = [c for c in chapters if c.attrs['value']]

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

            abs_url = self.last_visited_url.replace('book', 'reader')
            chap_url = abs_url + ('?c=%s' % a.attrs['value']) if a.has_attr('value') else self.home_url + a['href']
            self.chapters.append({
                'id': chap_id,
                'volume': 1,
                'url': chap_url,
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        # end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        contents = soup.select_one('div.reader-text')
        if contents is None:
            contents = soup.select_one('div.demo-txt')
        return contents.prettify()
    # end def
# end class
