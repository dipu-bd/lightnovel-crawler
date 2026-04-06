# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class LightNovelTV(WordpressTemplate):
    base_url = "https://lightnovel.tv/"
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="novel-author"]'
