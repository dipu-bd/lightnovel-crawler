# -*- coding: utf-8 -*-
import json
import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://meionovel.id/?s=%s&post_type=wp-manga&author=&artist=&release='
chapter_list_url = 'https://meionovel.id/wp-admin/admin-ajax.php'


class MeionovelCrawler(Crawler):
    base_url = 'https://meionovel.id/'

    # NOTE: Disabled because it takes too long
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('.c-tabs-item__content'):
    #         a = tab.select_one('.post-title h4 a')
    #         latest = tab.select_one('.latest-chap .chapter a').text
    #         votes = tab.select_one('.rating .total_votes').text
    #         results.append({
    #             'title': a.text.strip(),
    #             'url': self.absolute_url(a['href']),
    #             'info': '%s | Rating: %s' % (latest, votes),
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one('meta[property="og:title"]')['content'].split('-')[0]
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(soup.select_one('.summary_image img')['data-src'])
        logger.info('Novel cover: %s', self.novel_cover)

        possible_authors = [a.text.strip() for a in soup.select('.author-content a')]
        self.novel_author = ', '.join(filter(None, possible_authors))
        logger.info('Novel author: %s', self.novel_author)

        manga_id = soup.select_one('#manga-chapters-holder')['data-id']
        logger.info('Manga id: %s', manga_id)

        soup = self.post_soup(chapter_list_url, {
            'action': 'manga_get_chapters',
            'manga': manga_id,
        }, headers={
            'Origin': self.base_url,
            'Referer': self.novel_url,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })

        vols = set([])
        for a in reversed(soup.select('.wp-manga-chapter a')):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            vols.add(vol_id)
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url':  self.absolute_url(a['href']),
            })
        # end for

        self.volumes = [{'id': x} for x in vols]
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])

        contents = soup.select_one('div.text-left')

        for img in contents.findAll('img'):
            if img.has_attr('data-lazy-src'):
                src_url = img['data-lazy-src']
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        if contents.h3:
            contents.h3.extract()

        for codeblock in contents.findAll('div', {'class': 'code-block'}):
            codeblock.extract()

        return str(contents)
    # end def
# end class
