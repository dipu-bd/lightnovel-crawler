# -*- coding: utf-8 -*-
import logging
from concurrent.futures.thread import ThreadPoolExecutor
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://booknet.com/en/search?q=%s'
get_chapter_url = 'https://booknet.com/reader/get-page'


class LitnetCrawler(Crawler):
    base_url = [
        'https://booknet.com/',
    ]

    def initialize(self):
        self.home_url = 'https://booknet.com/'
        self.executor = ThreadPoolExecutor(1)
    # end def

    def search_novel(self, query):
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select('.book-item'):
            a = div.select_one('.book-title a')
            author = div.select_one('.author-wr a.author').text.strip()
            views = div.select_one('span.count-views').text.strip()
            favourites = div.select_one('span.count-favourites').text.strip()
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': 'Author: %s | %s views | %s favorites' % (author, views, favourites)
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.csrf_token = soup.select_one('meta[name="csrf-token"]')['content']
        self.csrf_param = soup.select_one('meta[name="csrf-param"]')['content']
        logger.info('%s: %s', self.csrf_param, self.csrf_token)

        self.novel_title = soup.select_one('h1.roboto').text.strip()
        logger.info('Novel title: %s', self.novel_title)

        img_src = soup.select_one('.book-view-cover img')
        if not img_src:
            img_src = soup.select_one('.book-cover img')
        # end if
        if img_src:
            self.novel_cover = self.absolute_url(img_src['src'])
        # end if
        logger.info('Novel cover: %s', self.novel_cover)

        author = soup.select_one('.book-view-info a.author')
        if not author:
            author = soup.select_one('.book-head-content a.book-autor')
        # end if
        if author:
            self.novel_author = author.text.strip()
        # end if
        logger.info('Novel author: %s', self.novel_author)

        chapters = soup.find('select', {'name': 'chapter'})
        if chapters is None:
            chapters = soup.select('.collapsible-body a.collection-item')
        else:
            chapters = chapters.find_all('option')
            chapters = [a for a in chapters if a.attrs['value']]
        # end if

        volumes = set([])
        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            volumes.add(vol_id)

            abs_url = self.last_visited_url.replace('/en/book/', '/en/reader/')
            chap_url = abs_url + ('?c=%s' % a.attrs['value'])
            self.chapters.append({
                'id': chap_id,
                'volume': 1,
                'url': chap_url,
                'chapter_id': a.attrs['value'],
            })
        # end for

        self.volumes = [{'id': x} for x in volumes]
    # end def

    def download_chapter_body(self, chapter):
        data = self._get_chapter_page(chapter)
        chapter['title'] = data['chapterTitle']
        content = data['data']

        for page in range(2, data['totalPages'] + 1):
            data = self._get_chapter_page(chapter, page)
            content += data['data']
        # end for

        return content
    # end def

    def _get_chapter_page(self, chapter, page=1):
        return self.post_json(get_chapter_url, data={
            'chapterId': int(chapter['chapter_id']),
            'page': page,
            self.csrf_param: self.csrf_token
        }, headers={
            'X-CSRF-Token': self.csrf_token,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        })
    # end def

# end class
