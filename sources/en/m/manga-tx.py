# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class MangaTXCrawler(WordpressMangaTemplate):
    base_url = ['https://manga-tx.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
