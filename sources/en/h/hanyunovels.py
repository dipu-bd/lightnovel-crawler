# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class HanyuNovels(WordpressTemplate):
    base_url = 'http://www.hanyunovels.site/'
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
