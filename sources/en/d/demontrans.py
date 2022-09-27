# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class DemonTranslations(Crawler):
    base_url = 'https://demontranslations.com/'

    def read_novel_info(self):
        logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "entry-title"}).text.strip()
        logger.info('Novel title: %s', self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one('div.entry-content p img')['data-orig-file'])
        logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = 'Demon Translations'
        logger.info('Novel author: %s', self.novel_author)

        # Extract volume-wise chapter entries
        # Stops external links being selected as chapters
        chapters = soup.select(
            'div.entry-content li [href*="demontranslations"]')

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

        body_parts = soup.select_one('div.entry-content')
        assert isinstance(body_parts, Tag), 'No chapter body'

        # Remoeves Nav Button from top and bottom of chapters.
        for content in body_parts.select("p"):
            for bad in ["Previous Chapter", "Table of Contents", "Next Chapter"]:
                if bad in content.text:
                    content.extract()

        return self.cleaner.extract_contents(body_parts)
