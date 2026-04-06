# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class NoobChanCrawler(WordpressMangaTemplate):
    base_url = ["https://noobchan.xyz/"]
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
