# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://novelfull.com/search?keyword=%s'

RE_VOLUME = r'(?:book|vol|volume) (\d+)'


class NovelFullCrawler(Crawler):
    base_url = [
        'http://novelfull.com/',
        'https://novelfull.com/',
    ]

    def search_novel(self, query):
        '''Gets a list of (title, url) matching the given query'''
        query = query.strip().lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select('#list-page .archive .list-truyen > .row'):
            a = div.select_one('.truyen-title a')
            info = div.select_one('.text-info a .chapter-text')
            results.append(
                {
                    'title': a.text.strip(),
                    'url': self.absolute_url(a['href']),
                    'info': info.text.strip() if info else '',
                }
            )
        # end for

        return results

    # end def

    def read_novel_info(self):
        '''Get novel title, autor, cover etc'''
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one('.info-holder .book img')
        self.novel_title = image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        authors = []
        for a in soup.select('.info-holder .info a'):
            if a['href'].startswith('/author/'):
                authors.append(a.text.strip())
            # end if
        # end for
        self.novel_author = ', '.join(authors)
        logger.info('Novel author: %s', self.novel_author)

        pagination_link = soup.select_one('#list-chapter .pagination .last a')
        page_count = int(str(pagination_link['data-page'])) if pagination_link else 0
        logger.info('Chapter list pages: %d' % page_count)

        logger.info('Getting chapters...')
        futures = [
            self.executor.submit(self.download_chapter_list, i + 1)
            for i in range(page_count + 1)
        ]

        self.chapters = []
        possible_volumes = set([])
        for f in futures:
            for chapter in f.result():
                chapter_id = len(self.chapters) + 1
                volume_id = (chapter_id - 1) // 100 + 1
                possible_volumes.add(volume_id)
                self.chapters.append({
                    'id': chapter_id,
                    'volume': volume_id,
                    'title': chapter['title'],
                    'url': chapter['url'],
                })
            # end for
        # end for

        self.volumes = [{'id': x} for x in possible_volumes]
    # end def

    def download_chapter_list(self, page):
        '''Download list of chapters and volumes.'''
        url = self.novel_url.split('?')[0].strip('/')
        url += '?page=%d&per-page=50' % page
        soup = self.get_soup(url)
        chapters = []
        for a in soup.select('ul.list-chapter li a'):
            title = a['title'].strip()
            chapters.append({
                'title': title,
                'url': self.absolute_url(a['href']),
            })
        # end for
        return chapters
    # end def

    def download_chapter_body(self, chapter):
        '''Download body of a single chapter and return as clean html format.'''
        logger.info('Downloading %s', chapter['url'])
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('div#chapter-content')
        self.blacklist_patterns += [
            'Read more chapter on NovelFull'
        ]
        self.bad_css += [
            'div[align="left"]',
            'img[src*="proxy?container=focus"]'
        ]
        return self.extract_contents(contents)
    # end def
# end class
