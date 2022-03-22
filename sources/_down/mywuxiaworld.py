# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://www.mywuxiaworld.com/search/result.html?searchkey=%s'


class MyWuxiaWorldCrawler(Crawler):
    base_url = [
        'https://www.mywuxiaworld.com/',
        'https://m.mywuxiaworld.com/',
    ]

    def initialize(self):
        self.home_url = 'https://www.mywuxiaworld.com/'
    # end def

    def search_novel(self, query):
        '''Gets a list of {title, url} matching the given query'''
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select('.pt-rank-detail'):
            a = div.select_one('.title a')
            info = div.select_one('.fl.lh100 a')['title']
            results.append({
                'title': a['title'],
                'url': self.absolute_url(a['href']),
                'info': info,
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        self.novel_url = self.novel_url.replace(
            'm.mywuxiaworld.com', 'www.mywuxiaworld.com')
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('div.pt-bookdetail .novelname a.bold')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title['title']
        logger.info('Novel title: %s', self.novel_title)

        possible_novel_author = soup.select_one('.pt-bookdetail a[href*="/author/"]')
        if possible_novel_author:
            self.novel_author = possible_novel_author['title']
        logger.info('Novel author: %s', self.novel_author)

        possible_image = soup.select_one('img.pt-bookdetail-img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        # Extract volume-wise chapter entries
        for a in soup.select('div.pt-chapter-cont-detail.full a'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({ 'id': vol_id })
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
        soup = self.get_soup(chapter['url'])
        contents = soup.select('div.pt-read-text p')
        body = [str(p) for p in contents if p.text.strip()]
        return '<p>' + '</p><p>'.join(body) + '</p>'
    # end def

# end class
