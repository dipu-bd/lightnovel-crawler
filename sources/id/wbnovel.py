# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class WBNovelCrawler(WordpressTemplate):
    base_url = "https://wbnovel.com/"
    chapter_body_selector = "div.text-left"
    madara_search_max_results = 20
