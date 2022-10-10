# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class NovelsEmperorCrawler(MangaStreamTemplate):
    base_url = ["https://novelsemperor.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Thank you for reading this story at novelsemperor.com",
                "immediately rushed \\(Campaign period:",
                "promotion, charge 100 and get 500 VIP coupons!",
            ]
        )
