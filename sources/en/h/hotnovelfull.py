# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class HotNovelFullCrawler(NovelFullTemplate):
    base_url = ["https://hotnovelfull.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tag_text_pairs.update(
            {
                "h4": [
                    r"Chapter \d+",
                    r"^\s*(Translator|Editor):.*$",
                ],
                "strong": r"This chapter upload first at NovelNext\.com",
            }
        )
