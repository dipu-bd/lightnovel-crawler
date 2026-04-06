# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class IsekaiScanEUCrawler(WordpressMangaTemplate):
    base_url = ["https://isekaiscan.eu/"]
    madara_search_quote_mode = "quote_plus"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
