# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://readonlinenovels.com/novel/search/?keywords=%s'


class ReadOnlineNovelsCrawler(Crawler):
    base_url = [
        'http://readonlinenovels.com/',
        'https://readonlinenovels.com/',
    ]

    def search_novel(self, query):
        soup = self.get_soup(search_url % query)

        results = []
        for div in soup.select('div.book-context'):
            a = div.select_one('a')
            title = a.select_one('h4 b').text.strip()
            info = div.select_one('div.update-info').text.strip()
            results.append({
                'title': title,
                'url': self.absolute_url(a['href']),
                'info': info,
            })
        return results

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.book-info div.title b')
        assert possible_title, 'No novel title'
        self.novel_title = possible_title.text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_author = soup.select_one(
            '.book-info div.title span').text.strip()
        logger.info('Novel author: %s', self.novel_author)

        possible_image = soup.select_one('div.book-img img')
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image['src'])
        logger.info('Novel cover: %s', self.novel_cover)

        for a in soup.select('div.slide-item a'):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({'id': vol_id})

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
            })

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('.read-context .reading_area')
        assert contents, 'No chapter contents found'
        return self.cleaner.extract_contents(contents)
