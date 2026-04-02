# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class FansTranslations(WordpressTemplate):
    base_url = 'https://fanstranslations.com/'
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
        self.taskman.init_executor(4)
