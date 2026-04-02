# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class MangaRosieCrawler(WordpressMangaTemplate):
    base_url = ['https://mangarosie.me/', 'https://mangarosie.love/', 'https://toon69.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
