# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class KingMangaCrawler(WordpressMangaTemplate):
    base_url = ['https://king-manga.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
