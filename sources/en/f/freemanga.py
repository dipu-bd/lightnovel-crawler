# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class FreeMangaCrawler(WordpressMangaTemplate):
    base_url = ["https://freemanga.me/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
