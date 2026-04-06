# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class KissMangaCrawler(WordpressMangaTemplate):
    base_url = ["https://kissmanga.in/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
