# -*- coding: utf-8 -*-

import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Miraslation(Crawler):
    base_url = [
        'https://miraslation.net/',
        'https://www.miraslation.net/',
    ]

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        title = soup.select_one('h1.entry-title').text
        self.novel_title = title.rsplit(' ', 1)[0]
        logger.debug('Novel title = %s', self.novel_title)

        # NOTE: Site does not have covers.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('div.entry-content p strong img')['data-orig-file'])
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = "Translated by Mira's Cocktail"
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'article.posts-entry p [href*="miraslation.net/novels/"]')

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({'id': vol_id})

            self.chapters.append({
                'id': chap_id,
                'volume': vol_id,
                'url': self.absolute_url(a['href']),
                'title': a.text.strip() or ('Chapter %d' % chap_id),
            })

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])

        body_parts = soup.select_one('.entry-content')
        assert body_parts, 'No chapter body'

        for content in body_parts.select("p"):
            for bad in ["Table of Contents", "Previous Chapter", "Next Chapter", " | "]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
