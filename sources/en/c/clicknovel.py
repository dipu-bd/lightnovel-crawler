# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ClickNovel(WordpressTemplate):
    base_url = 'https://clicknovel.net/'
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="authors"]'
