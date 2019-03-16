#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [mtled-novels.com](https://mtled-novels.com/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('MTLED-NOVELS')
search_url = 'https://mtled-novels.com/search_novel.php?q=%s'


class MtledNovelsCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select('.card .row .col-lg-2 a')[:5]:
            url = self.absolute_url(a['href'])
            results.append({
                'url': url,
                'title': a.img['alt'],
                'info': self.search_novel_info(url),
            })
        # end for

        return results
    # end def

    def search_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        chapters = soup.select('#tab-profile-2 a.chapters')
        info = '%d chapters' % len(chapters)
        if len(chapters) > 0:
            info += ' | Latest: %s' % chapters[-1].text.strip()
        # end if

        return info
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.profile__img img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Downloaded from mtled-novels.com"
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.select('div#tab-profile-2 a')

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

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        if soup.h1.text.strip():
            chapter['title'] = soup.h1.text.strip()
        else:
            chapter['title'] = chapter['title']
        # end if

        self.blacklist_patterns = [
            r'^translat(ed by|or)',
            r'(volume|chapter) .?\d+',
        ]

        contents = soup.select('div.translated p')
        # print(contents)
        for p in contents:
            for span in p.findAll('span'):
                span.unwrap()
            # end for
        # end for
        # print(contents)
        # self.clean_contents(contents)
        #body = contents.select('p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
