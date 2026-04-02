# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class IsekaiScanCrawler(WordpressMangaTemplate):
    base_url = ['https://isekaiscan.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
