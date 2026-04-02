# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class MangaReadCrawler(WordpressMangaTemplate):
    base_url = ['https://www.mangaread.org/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
