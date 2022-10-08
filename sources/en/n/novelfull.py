# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelFullCrawler(NovelFullTemplate):
    base_url = [
        "http://novelfull.com/",
        "https://novelfull.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                'div[align="left"]',
                'img[src*="proxy?container=focus"]',
            ]
        )
