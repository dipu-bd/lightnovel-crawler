# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class OneKissNovelCrawler(WordpressTemplate):
    base_url = ["https://1stkissnovel.org/", "https://1stkissnovel.love/"]
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
