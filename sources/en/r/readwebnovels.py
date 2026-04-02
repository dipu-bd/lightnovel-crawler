# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ReadWebNovels(WordpressTemplate):
    base_url = 'https://readwebnovels.net/'
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'
