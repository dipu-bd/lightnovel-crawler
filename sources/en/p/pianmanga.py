# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class PianMangaCrawler(WordpressMangaTemplate):
    base_url = ["https://pianmanga.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
