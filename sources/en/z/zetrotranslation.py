# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ZetroTranslationCrawler(WordpressTemplate):
    base_url = ["https://zetrotranslation.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3", "script"])
        self.cleaner.bad_css.update([".code-block", ".adsbygoogle"])
