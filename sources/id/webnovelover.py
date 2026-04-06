# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class WebNoveLover(WordpressTemplate):
    base_url = "https://www.webnovelover.com/"
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'
