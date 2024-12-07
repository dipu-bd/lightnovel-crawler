# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class CentralNovelCrawler(MangaStreamTemplate):
    base_url = ["https://centralnovel.com/"]

    def initialize(self) -> None:
        self.init_executor(ratelimit=2.99)
