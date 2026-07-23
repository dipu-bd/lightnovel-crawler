# -*- coding: utf-8 -*-
import logging

from lncrawl.core import PageSoup
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelNextCrawler(NovelFullTemplate):
    base_url = ["https://novelnext.com/", "https://novelnext.dramanovels.io/"]
    request_rate_limit = 0.2

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

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        return soup.select_one("#chr-content, #chapter-content")
