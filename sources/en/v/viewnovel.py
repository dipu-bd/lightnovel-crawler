# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ViewNovel(WordpressTemplate):
    base_url = "https://viewnovel.net/"
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="authors"]'
