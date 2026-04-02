# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class ZinMangaCrawler(WordpressMangaTemplate):
    base_url = ['https://zinmanga.com/']

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
