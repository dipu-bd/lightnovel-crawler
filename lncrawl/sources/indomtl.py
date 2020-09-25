#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

short_page_url = 'https://indomtl.com/?p=%s'
search_url = 'https://indomtl.com/wp-admin/admin-ajax.php?action=mtl_auto_suggest&q=%s'
chapter_list_url = 'https://indomtl.com/wp-admin/admin-ajax.php?action=mtl_chapter_json&id_novel=%s&view_all=yes&moreItemsPageIndex=%d'


class IndoMTLCrawler(Crawler):
    base_url = 'https://indomtl.com/'

    def search_novel(self, query):
        url = search_url % quote(query.lower())
        logger.debug('Visiting %s', url)
        data = self.get_json(url)

        results = []
        for item in data['items'][0]['results']:
            results.append({
                'url': short_page_url % item['id'],
                'title': re.sub(r'<\/?strong>', '', item['title']),
            })
        # end for
        return results
    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select('nav.breadcrumb li a span')[-1].text
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('.kn-img amp-img')['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for a in soup.select('.globalnovelinfopartvalue a'):
            if a['href'].startswith('https://indomtl.com/penulis/'):
                self.novel_author = a.text.strip()
                break
            # end if
        # end for
        logger.info('Novel author: %s', self.novel_author)

        novel_id = soup.select_one('form#rating input[name=id_novel]')['value']
        logger.info('Novel Id: %s', novel_id)

        ch_page = 0
        hasMore = True
        all_items = []
        while hasMore:
            url = chapter_list_url % (novel_id, ch_page)
            ch_page += 1
            logger.debug('Visiting %s', url)
            data = self.get_json(url)
            all_items += data['items']
            hasMore = data['hasMorePages'] == 1
        # end while

        for item in reversed(all_items):
            self.chapters.append({
                'id': len(self.chapters) + 1,
                'volume': len(self.chapters) // 100 + 1,
                'title': item['title'],
                'url': item['permalink'],
            })
        # end for
        logger.debug(self.chapters)

        self.volumes = [{'id': x + 1}
                        for x in range(len(self.chapters) // 100 + 1)]
        logger.debug(self.volumes)

        logger.debug('%d volumes & %d chapters found',
                     len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select('article div.entry-content p.indo')
        contents = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(contents) + '</p>'
    # end def
# end class
