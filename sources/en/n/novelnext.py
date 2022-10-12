# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelNextCrawler(NovelFullTemplate):
    base_url = ["https://novelnext.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tag_text_pairs.update(
            {
                "h4": [
                    r"Chapter \d+",
                    r"^\s*(Translator|Editor):.*$",
                ],
                "p": [
                    r"^\s*(Translator|Editor):.*$",
                    r"Bookmark this website \( ",
                    r"\)  to update the latest novels\.",
                ],
                "strong": r"NovelNext\.com",
            }
        )
