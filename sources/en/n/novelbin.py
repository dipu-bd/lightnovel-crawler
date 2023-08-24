# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelbinCrawler(NovelFullTemplate):
    base_url = ["https://novelbin.com/"]

    def initialize(self) -> None:
        self.init_executor(ratelimit=0.99)
