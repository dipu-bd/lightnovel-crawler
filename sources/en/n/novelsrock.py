# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelsRockCrawler(WordpressTemplate):
    base_url = "https://novelsrock.com/"
    madara_search_quote_mode = "quote_plus"
