# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class VipNovel(WordpressTemplate):
    base_url = "https://vipnovel.com/"
    chapter_body_selector = "div.text-left"
    madara_search_max_results = 20
