#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote, urlparse
from ..utils.crawler import Crawler

logger = logging.getLogger('NOVELRAW_BLOGSPOT')

chapter_list_url = 'https://novelraw.blogspot.com/feeds/posts/default/-/%s?alt=json&start-index=1&max-results=999999&orderby=published'


class NovelRawCrawler(Crawler):
    def read_novel_info(self):
        # Determine cannonical novel name
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        for script in soup.select('#tgtPost script'):
            text = script.text.strip()
            pre = 'var label="'
            post = '";'
            if text.startswith(pre) and text.endswith(post):
                self.novel_title = text[len(pre):-len(post)]
                break
            # end if
        # end for
        logger.info('Novel title: %s', self.novel_title)

        data = self.get_json(chapter_list_url % self.novel_title)
        self.novel_author = ', '.join([
            x['name']['$t'] for x in data['feed']['author']
        ])
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = soup.select_one('#tgtPost .separator img')['src']
        logger.info('Novel cover: %s', self.novel_cover)

        for entry in reversed(data['feed']['entry']):
            possible_urls = [
                x['href'] for x in entry['link'] if x['rel'] == 'alternate'
            ]
            if not len(possible_urls):
                continue
            # end if
            self.chapters.append({
                'id': len(self.chapters) + 1,
                'volume': len(self.chapters) // 100 + 1,
                'title': entry['title']['$t'],
                'url': possible_urls[0]
            })
        # end for
        logger.debug(self.chapters)

        self.volumes = [
            {'id': x + 1} for x in range(len(self.chapters) // 100 + 1)
        ]
        logger.debug(self.volumes)

        logger.info('%d volumes and %d chapters found',
                    len(self.volumes), len(self.chapters))
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = self.extract_contents(soup.select_one('#tgtPost'))
        return '<p>' + '</p><p>'.join(contents) + '</p>'
    # end def
# end class
