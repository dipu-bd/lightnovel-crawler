# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

import json

logger = logging.getLogger(__name__)
next_url = '%s_next/data/%s/en%s'


class NovelSalaCrawler(Crawler):
    base_url = [
        'https://novelsala.com/'
    ]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        script_data = soup.select_one('script[id="__NEXT_DATA__"]').get_text()
        json_data = json.loads(script_data)

        buildId = json_data['buildId']
        book_data = (json_data['props']['pageProps']['relayData'][0][1]
                     ['data']['book']['edges'][0]['node'])

        self.novel_title = book_data['title']
        self.novel_cover = book_data['coverLg']
        self.novel_author = book_data['author']['name']

        logger.info("Novel author: %s", self.novel_author)

        chapters_count = book_data['numChapters']
        for cid in range(chapters_count):
            chap_id = cid + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.novel_url.rstrip('/') + f'/chapter-{chap_id}/',
                    "chapter_json_url": next_url % (self.home_url, buildId, book_data['url']) + f"chapter-{chap_id}.json",
                }
            )

    def download_chapter_body(self, chapter):
        chapter_json = self.get_json(chapter["chapter_json_url"])
        chapter_data = chapter_json['pageProps']['relayData'][0][1]['data']['chapter2']

        chapter['title'] = chapter_data['title']
        content = chapter_data['contentHtml']

        return content
