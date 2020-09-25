# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures
from urllib.parse import quote, urlparse

from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_limit = 150  # currently supports maximum of 150
chapter_list_url = 'https://novelraw.blogspot.com/feeds/posts/default/-/%s?alt=json&start-index=%d&max-results=' + \
    str(chapter_list_limit) + '&orderby=published'


class NovelRawCrawler(Crawler):
    base_url = 'https://novelraw.blogspot.com/'

    def read_novel_info(self):
        # Determine cannonical novel name
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        for script in soup.select('script[type="text/javaScript"]'):
            if not script.contents:
                continue

            text = re.findall(r'var label="([^"]+)";', script.string)
            if len(text) == 1:
                self.novel_title = text[0].strip()
                break
            # end if
        # end for
        logger.info('Novel title: %s', self.novel_title)

        url = chapter_list_url % (self.novel_title, 1)
        logger.debug('Visiting %s', url)
        data = self.get_json(url)
        self.novel_author = ', '.join([
            x['name']['$t'] for x in data['feed']['author']
        ])
        logger.info('Novel author: %s', self.novel_author)

        self.novel_cover = soup.select_one('#tgtPost .separator img')['src']
        logger.info('Novel cover: %s', self.novel_cover)

        total_chapters = int(data['feed']['openSearch$totalResults']['$t'])
        logger.info('Total chapters = %d', total_chapters)

        logger.info('Getting chapters...')
        futures_to_check = {
            self.executor.submit(
                self.download_chapter_list,
                i,
            ): str(i)
            for i in range(1, total_chapters + 1, chapter_list_limit)
        }
        all_entry = dict()
        for future in futures.as_completed(futures_to_check):
            page = int(futures_to_check[future])
            all_entry[page] = future.result()
        # end for

        for page in reversed(sorted(all_entry.keys())):
            for entry in reversed(all_entry[page]):
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
        # end for

        self.volumes = [
            {'id': x + 1} for x in range(len(self.chapters) // 100 + 1)
        ]
    # end def

    def download_chapter_list(self, index):
        url = chapter_list_url % (self.novel_title, index)
        logger.debug('Visiting %s', url)
        data = self.get_json(url)
        return data['feed']['entry']
    # end def

    def download_chapter_body(self, chapter):
        logger.info('Visiting %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = self.extract_contents(soup.select_one('#tgtPost'))
        return '<p>' + '</p><p>'.join(contents) + '</p>'
    # end def
# end class
