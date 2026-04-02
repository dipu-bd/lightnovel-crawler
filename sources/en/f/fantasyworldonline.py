# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class FantasyWorldOnline(WordpressTemplate):
    base_url = ['https://www.f-w-o.com/', 'https://f-w-o.com/']
    chapter_body_selector = "div.text-left"
    novel_author_selector = '.author-content a[href*="novel-author"]'
