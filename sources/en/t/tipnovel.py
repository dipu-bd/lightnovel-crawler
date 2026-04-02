# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class TipNovel(WordpressTemplate):
    base_url = 'https://tipnovel.com/'
    chapter_body_selector = "div.text-left"
