# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class PeryInfo(WordpressTemplate):
    base_url = 'https://pery.info/'
    chapter_body_selector = "div.text-left"
