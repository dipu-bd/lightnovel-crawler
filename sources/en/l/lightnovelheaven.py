# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class LightNovelHeaven(WordpressTemplate):
    base_url = 'https://lightnovelheaven.com/'
    madara_body_from_paragraphs = True
    madara_search_quote_mode = "quote_plus"
