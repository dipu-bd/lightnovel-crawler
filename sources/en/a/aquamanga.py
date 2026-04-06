# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class AquaMangaCrawler(WordpressMangaTemplate):
    base_url = ["https://aquamanga.com/", "https://aquamanga.org/", "https://aquareader.net/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
