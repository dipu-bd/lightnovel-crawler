# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class OppaTranslationsCrawler(Crawler):
    base_url = ['https://www.oppatranslations.com/']

    def initialize(self):
        self.home_url = 'https://www.oppatranslations.com/'
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)
        self.novel_title = soup.select_one(
            'header.entry-header h1.entry-title').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        possible_authors = soup.select('div.entry-content p strong')
        for author in possible_authors:
            if author and author.text.strip().startswith('Author :'):
                self.novel_author = author.text.strip().replace('Author :', '')
                break
        logger.info('Novel author: %s', self.novel_author)

        try:
            self.novel_cover = self.absolute_url(
                soup.select_one('div.entry-content img')['src'])
        except Exception:
            pass
        # end try
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        for a in soup.select('div.entry-content p a'):
            if self.novel_url[15:] in a['href']:
                chap_id = len(self.chapters) + 1
                if len(self.chapters) % 100 == 0:
                    vol_id = chap_id // 100 + 1
                    vol_title = 'Volume ' + str(vol_id)
                    self.volumes.append({
                        'id': vol_id,
                        'title': vol_title,
                    })
                # end if
                self.chapters.append({
                    'id': chap_id,
                    'volume': vol_id,
                    'title': a.text.strip(),
                    'url':  self.absolute_url(a['href']),
                })
        # end for

    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('div.entry-content')

        for p in reversed(contents.select('p')):
            if p.find('a') and 'TOC' in p.text:
                p.extract()
        # end for

        contents.select_one('div center').extract()

        return re.sub(u'[⺀-⺙⺛-⻳⼀-⿕々〇〡-〩〸-〺〻㐀-䶵一-鿃豈-鶴侮-頻並-龎]',
                      '', str(contents), flags=re.UNICODE)
    # end def

# end class
