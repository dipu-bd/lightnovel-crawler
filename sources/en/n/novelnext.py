# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelNextCrawler(NovelFullTemplate):
    base_url = ["https://novelnext.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Bookmark this website ( ",
                "NovelNext.com",
                " ) to update the latest novels."
                ]
        )