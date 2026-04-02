# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class RandomNovelCrawler(WordpressTemplate):
    base_url = ['https://randomnovel.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
