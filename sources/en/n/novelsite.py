# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelSiteCrawler(WordpressTemplate):
    base_url = 'https://novelsite.net/'
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="novel-author"]'
    madara_search_max_results = 20
