# -*- coding: utf-8 -*-

import logging
from lncrawl.core.crawler import Crawler
from sources import madara_crawler as madara

logger = logging.getLogger(__name__)


class MangaRockTeamCrawler(Crawler):
    has_manga = True
    base_url = [
        'https://mangarockteam.com/'
    ]

    def initialize(self) -> None:
        madara.initialize(self)

    def search_novel(self, query):
        return madara.search_novel(self, query)

    def read_novel_info(self):
        madara.read_novel_info(self)

    def download_chapter_body(self, chapter):
        return madara.download_chapter_body(self, chapter)
