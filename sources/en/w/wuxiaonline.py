# -*- coding: utf-8 -*-
import json
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://wuxiaworld.online/search.ajax?type=&query=%s'


class WuxiaOnlineCrawler(Crawler):
    base_url = 'https://wuxiaworld.online/'

    # NOTE: DISABLING DUE TO CLOUDEFLARE CAPTCHA CHALLENGE
    # def search_novel(self, query):
    #     '''Gets a list of {title, url} matching the given query'''
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for novel in soup.select('li'):
    #         a = novel.select_one('.resultname a')
    #         info = novel.select_one('a:nth-of-type(2)')
    #         info = info.text.strip() if info else ''
    #         results.append({
    #             'title': a.text.strip(),
    #             'url': self.absolute_url(a['href']),
    #             'info': 'Latest: %s' % info,
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        url = self.novel_url
        logger.debug('Visiting %s', url)
        soup = self.get_soup(url)
        self.novel_title = soup.select_one('h1.entry-title').text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one('div.entry-header > div.truyen_if_wrap > ul > li:nth-child(2)').text
        logger.info('%s', self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one('.info_image img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        last_vol = -1
        for a in reversed(soup.select('.chapter-list .row span a')):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + (chap_id - 1) // 100
            volume = {'id': vol_id, 'title': ''}
            if last_vol != vol_id:
                self.volumes.append(volume)
                last_vol = vol_id
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a['title'],
                'url':  self.absolute_url(a['href']),
            })
        # end for

    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        parts = soup.select_one('#list_chapter .content-area')
        return self.extract_contents(parts)
    # end def
# end class
