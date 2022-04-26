# -*- coding: utf-8 -*-

import logging
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

class AllNovelCrawler(Crawler):
    base_url = [
        'https://allnovel.org/',
        'https://www.allnovel.org/',
    ]

    def initialize(self) -> None:
        self.home_url = self.base_url[0]
        self.cleaner.blacklist_patterns.update([
            'If you find any errors ( broken links, non-standard content, etc.. ), Please let us know < report chapter > so we can fix it as soon as possible.'
        ])
    # end def

    def search_novel(self, query):
        soup = self.get_soup(self.home_url + 'search?keyword=' + quote(query))

        results = []
        for div in soup.select('.list-truyen > .row'):
            a = div.select_one('.truyen-title a')
            if not isinstance(a, Tag):
                continue
            # end if
            info = div.select_one('.text-info .chapter-text')
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
        soup = self.get_soup(self.novel_url)

        image = soup.select_one('.info-holder .book img')
        assert isinstance(image, Tag), 'No title found'

        self.novel_title = image['alt']
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        authors = soup.select('.info-holder .info a[href*="/author/"]')
        self.novel_author = ', '.join([a.text.strip() for a in authors])
        logger.info('Novel author: %s', self.novel_author)

        logger.info('Getting chapters...')

        # NOTE: old way to get chapter list by visiting each pages
        # page_count = 0
        # pagination_link = soup.select_one('#list-chapter .pagination .last a')
        # if isinstance(pagination_link, Tag):
        #     page_count = int(str(pagination_link['data-page']))
        # logger.info('Chapter list pages: %d' % page_count)

        # futures = []
        # for page in range(1, page_count + 2):
        #     if page == 1:
        #         f = self.executor.submit(lambda: soup)
        #     else:
        #         url = self.novel_url.split('?')[0].strip('/')
        #         url += '?page=%d' % page
        #         f = self.executor.submit(self.get_soup, url)
        #     # end if
        #     futures.append(f)
        # # end for

        # for i, f in enumerate(futures):
        #     try:
        #         soup = f.result()
        #     except KeyboardInterrupt:
        #         c = len([f.cancel() for f in futures[i:]])
        #         logger.info('Cancelled remaining %d jobs', c)
        #     # end try
        #     for a in soup.select('ul.list-chapter li a'):
        #         chap_id = len(self.chapters) + 1
        #         vol_id = 1 + len(self.chapters) // 100
        #         if len(self.volumes) < vol_id:
        #             self.volumes.append({ 'id': vol_id })
        #         # end if
        #         self.chapters.append({
        #             'id': chap_id,
        #             'volume': vol_id,
        #             'title': a['title'],
        #             'url': self.absolute_url(a['href']),
        #         })
        #     # end for
        # # end for
        
        possible_id = soup.select_one('input#truyen-id')
        assert possible_id, 'No novel id'
        self.novel_id = possible_id['value']
        soup = self.get_soup(self.home_url + 'ajax-chapter-option?novelId=%s' % self.novel_id)
        for opt in soup.select('select option'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
            # end if
            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': opt.text,
                'url': self.absolute_url(opt['value']),
            })
        # end for
    # end def

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        content = soup.select_one('div#chapter-content')

        assert isinstance(content, Tag), 'No chapter content'
        for child in content.contents:
            child.extract()
            if isinstance(child, Tag) and child.name == 'h3':
                break
            # end if
        # end for

        return self.cleaner.extract_contents(content)
    # end def
# end class
