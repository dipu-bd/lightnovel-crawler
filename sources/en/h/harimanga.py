# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class HariMangaCrawler(WordpressMangaTemplate):
    base_url = ["https://harimanga.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
