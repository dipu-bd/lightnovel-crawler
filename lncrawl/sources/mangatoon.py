# -*- coding: utf-8 -*-
import json
import logging
import re
import ast
from ..utils.crawler import Crawler

logger = logging.getLogger('MANGATOON_MOBI')

book_url = 'https://mangatoon.mobi/%s/detail/%s/episodes'
search_url = 'https://mangatoon.mobi/%s/search?word=%s'


class MangatoonMobiCrawler(Crawler):
    base_url = 'https://mangatoon.mobi/'

    def initialize(self):
        self.home_url = 'https://mangatoon.mobi'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        self.novel_id = self.novel_url.split('/')[5]
        logger.info('Novel Id: %s', self.novel_id)

        novel_region = self.novel_url.split('/')[3]

        self.novel_url = book_url % (novel_region,self.novel_id)
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title =soup.select_one('h1.comics-title').text
        logger.info('Novel title: %s', self.novel_title)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('.detail-top-right img')['src'])
            logger.info('Novel cover: %s', self.novel_cover)
        except Exception:
            logger.debug('Failed to get cover: %s', self.novel_url)
        # end try

        self.novel_author = soup.select_one('.created-by').text
        logger.info('Novel author: %s', self.novel_author)

        for a in soup.select('a.episode-item'):
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
                'title': a.select_one('.episode-title').text.strip() or ('Chapter %d' % chap_id),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        script = soup.find("script", text=re.compile("initialValue\s+="))
        initialValue = re.search('var initialValue = (?P<value>.*);', script.string)
        content = initialValue.group('value')
        chapter_content = ast.literal_eval(content)
        chapter_content = [p.replace('\-', '-') for p in chapter_content]


        text = '<p>' + '</p><p>'.join(chapter_content) + '</p>'
        # end if
        return text.strip()
    # end def
# end class
