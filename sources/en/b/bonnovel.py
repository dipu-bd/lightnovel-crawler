# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class BonNovelCrawler(WordpressTemplate):
    base_url = ['https://bonnovel.com/']
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
