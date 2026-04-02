# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class Amnesiactl(WordpressTemplate):
    base_url = 'https://amnesiactl.com/'
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="novel-author"]'
