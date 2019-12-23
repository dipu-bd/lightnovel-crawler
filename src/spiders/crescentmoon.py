#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [crescentmoon.blog](https://crescentmoon.blog/).
"""
import json
import logging
import re

from ..utils.crawler import Crawler

logger = logging.getLogger('CRESCENTMOON')


class CrescentMoonCrawler(Crawler):

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.entry-content p a')['href'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('div.entry-content p')[2].text.strip()
        logger.info('Novel author: %s', self.novel_author)

        a = soup.select('div.entry-content p')
        for idx, item in enumerate(a):
            if "table of contents" in item.text.strip().lower():
                toc = a[idx+1]

        chapters = toc.findAll('a')

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
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        # if soup.find("h1", {"class": "entry-title"}).text.strip():
        #    chapter['title'] = soup.find("h1", {"class": "entry-title"}).text.strip()
        # else:
        #    chapter['title'] = chapter['title']
        # end if

        #contents = soup.select('div.entry-content p')
        #contents = contents[:-1]
        #body = self.extract_contents(contents)
        # return '<p>' + '</p><p>'.join(body) + '</p>'
        # return contents.prettify()
        body = []
        contents = soup.select('div.entry-content p')
        contents = contents[:-1]
        for p in contents:
            para = ' '.join(self.extract_contents(p))
            if len(para):
                body.append(para)
            # end if
        # end for

        return '<p>%s</p>' % '</p><p>'.join(body)
    # end def
# end class
