#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [id.mtlnovel.com](https://id.mtlnovel.com/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('IDMTLNOVEL')
search_url = 'https://id.mtlnovel.com/wp-admin/admin-ajax.php?action=autosuggest&q=%s'

class IdMtlnovelCrawler(Crawler):
    def search_novel(self, query):
        query = query.lower().replace(' ', '%20')
        #soup = self.get_soup(search_url % query)

        list_url = search_url % query
        data = self.get_json(list_url)['items'][0]['results']

        results = []
        for item in data:
            url = self.absolute_url("https://id.mtlnovel.com/?p=%s" % item['id'])
            results.append({
                'url': url,
                'title': item['title'],
                'info': self.search_novel_info(url),
            })
        # end for

        return results
    # end def

    def search_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)

        chapters = soup.select('div.info-wrap div')[1].text.replace('Chapters','')
        info = '%s chapters' % chapters
        #if len(chapters) > 0:
        #    info += ' | Latest: %s' % chapters[-1].text.strip()
        # end if

        return info
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('h1.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select('div.nov-head amp-img')[1]['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = soup.select('table.info tr')[3].find('a').text
        logger.info('Novel author: %s', self.novel_author)

        chapter_list = soup.select('div.ch-list amp-list')

        for item in chapter_list:
            data = self.get_json(item['src'])
            for chapter in data['items']:
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
                    'url':  chapter['permalink'],
                    'title': chapter['title'] or ('Chapter %d' % chap_id),
                })
            # end for
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        contents = soup.select('div.post-content p.en')
        # print(contents)
        #for p in contents:
        #    for span in p.findAll('span'):
        #        span.unwrap()
            # end for
        # end for
        # print(contents)
        # self.clean_contents(contents)
        #body = contents.select('p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
