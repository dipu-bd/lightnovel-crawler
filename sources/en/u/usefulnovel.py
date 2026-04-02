# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class UsefulNovelCrawler(WordpressTemplate):
    base_url = ['https://usefulnovel.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
