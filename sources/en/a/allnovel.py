# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class AllNovelCrawler(NovelFullTemplate):
    base_url = [
        "https://allnovel.org/",
        "https://www.allnovel.org/",
        "https://allnovelxo.com/"
    ]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
