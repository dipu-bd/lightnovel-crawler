#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [mtlnovel.com](https://www.mtlnovel.com/).
"""
import json
import logging
import re
from ..utils.crawler import Crawler

logger = logging.getLogger('WORDEXCERPT')
search_url = 'https://wordexcerpt.com/?s=%s&post_type=wp-manga'


class WordExcerptCrawler(Crawler):

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('div.post-title h1').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.summary_image a img')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = 'Author : %s, Translator : %s' % (soup.select_one('div.author-content a').text,soup.select_one('div.artist-content a').text)
        logger.info('Novel author: %s', self.novel_author)

        if soup.select('ul.sub-chap'):
            volume_list = soup.select('ul.main li.parent')
            last_vol = -1
            volume = {'id': 0, 'title': 'Volume 1', }
            for item in volume_list:
                vol = volume.copy()
                vol['id'] += 1
                vol_title = 'Volume ' + str(vol['id'])
                volume = vol
                chapter_list = item.select('li.wp-manga-chapter a')
                chapter_list.reverse()
                for chapter in chapter_list:
                    chap_id = len(self.chapters) + 1
                    self.chapters.append({
                        'id': chap_id,
                        'volume': volume['id'],
                        'url':  chapter['href'],
                        'title': chapter.text.strip() or ('Chapter %d' % chap_id),
                    })
                    if last_vol != volume['id']:
                        last_vol = volume['id']
                        self.volumes.append(volume)
                # end for
            # end for
        else:
            chapter_list = soup.select('li.wp-manga-chapter a')
            chapter_list.reverse()
            for chapter in chapter_list:
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
                    'url':  chapter['href'],
                    'title': chapter.text.strip() or ('Chapter %d' % chap_id),
                })
            # end for
        # end if
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        logger.debug(soup.title.string)

        contents = soup.select('div.text-left p')
        
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def
# end class
