# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class FreeFullNovelCrawler(WordpressTemplate):
    base_url = ["https://freefullnovel.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
