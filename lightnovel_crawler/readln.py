#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Crawler for [readlightnovel.org](https://www.readlightnovel.org/).
"""
import json
import logging
import re
from bs4 import BeautifulSoup
from .utils.crawler import Crawler

logger = logging.getLogger('READLIGHTNOVEL')

home_url = 'https://www.readlightnovel.org/'

class ReadLightNovelCrawler(Crawler):
    @property
    def supports_login(self):
        '''Whether the crawler supports login() and logout method'''
        return False
    # end def

    def login(self, email, password):
        pass
    # end def

    def logout(self):
        pass
    # end def

    def read_novel_info(self, url):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', url)
        response = self.get_response(url)
        soup = BeautifulSoup(response.text, 'lxml')

        self.novel_title = soup.select_one('.block-title h1').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = soup.find('img', {"alt" : self.novel_title})['src']
        logger.info('Novel cover: %s', self.novel_cover)
        
        try:
            self.novel_author = soup.select_one("a[href*=author]").text.strip().title()
        except:
            pass
        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('.chapters .chapter-chs li a'):
            chap_id = len(self.chapters) + 1
            if len(self.chapters) % 100 == 0:
                vol_id =  chap_id//100 +1
                vol_title =  'Volume ' + str(vol_id)
                self.volumes.append({
                    'id': vol_id,
                    'title': vol_title,
                })
            #end if
            href = a['href'].strip()
            if href.startswith('/'):
                href = url + href
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url':  href,
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })
        #end for

        logger.debug(self.chapters)
        logger.debug('%d chapters found', len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        response = self.get_response(chapter['url'])
        soup = BeautifulSoup(response.text, 'lxml')

        body_parts = soup.select_one('.chapter-content3 .desc')
        body = self.extract_text_from(body_parts.contents)
        body = [x for x in body if len(x) and self.not_blacklisted(x)]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

    def extract_text_from(self, contents):
        body = []
        for elem in contents:
            if not elem.name:
                body.append(str(elem).strip())
            elif ['h3', 'p'].count(elem.name):
                body += self.extract_text_from(elem.contents)
            elif ['strong', 'p', 'span', 'b', 'i'].count(elem.name):
                elem.name = 'span'
                body.append(str(elem).strip())
            # end if
        # end for
        return body
    # end def

    def not_blacklisted(self, text):
        blacklist = [
            r'^(volume|chapter) .?\d+$',
        ]
        for item in blacklist:
            if re.search(item, text, re.IGNORECASE):
                return False
            # end if
        # end for
        return True
    # end def
# end class