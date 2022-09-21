# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class CeuNovelCrawler(Crawler):
    base_url = [
        'https://www.ceunovel.com/',
    ]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(['div', 'h1', 'h2'])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('.crumbs > span:nth-of-type(2)')
        if possible_title:
            self.novel_title = possible_title.get_text()

        logger.info('Novel title: %s', self.novel_title)

        for p in soup.select('div:not([class], [id]) > p'):
            text = p.text.strip()
            if 'Author/Translator' in text:
                self.novel_author = text.split(':')[1]
                break

        logger.info('Novel author: %s', self.novel_author)

        prev_vol_id = None
        has_volumes = False

        for a in reversed(soup.select("div > li > a")):
            chap_id = 1 + len(self.chapters)
            title = a.text.strip()

            for title_data in title.split(' - '):
                if 'Volume' in title_data:
                    has_volumes = True
                    vol_id = int(title_data.split()[1])
                    if prev_vol_id != vol_id:
                        prev_vol_id = vol_id
                        self.volumes.append({'id': vol_id})
                    break

            if not has_volumes:
                vol_id = 1 + len(self.chapters) // 100
                if chap_id % 100 == 1:
                    self.volumes.append({'id': vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": title,
                    "url": self.absolute_url(a['href']),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter['url'])
        contents = soup.select_one('#contentatt')
        return self.cleaner.extract_contents(contents)
