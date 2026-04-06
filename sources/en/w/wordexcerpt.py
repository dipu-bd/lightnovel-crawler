# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class WordExcerptCrawler(WordpressTemplate):
    base_url = ["https://wordexcerpt.com/", "https://wordexcerpt.org/"]
    chapter_body_selector = "div.text-left"
