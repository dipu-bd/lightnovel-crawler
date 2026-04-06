# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class MangaWeebsCrawler(WordpressMangaTemplate):
    base_url = ["https://mangaweebs.in/", "https://www.mangaweebs.in/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
