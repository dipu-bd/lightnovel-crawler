# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class OverABook(WordpressTemplate):
    base_url = 'https://overabook.com/'
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="novel-author"]'
