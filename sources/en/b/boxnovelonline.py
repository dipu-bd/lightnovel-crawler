# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class BoxNovelOnline(WordpressTemplate):
    base_url = 'https://boxnovel.online/'
    chapter_body_selector = "div.text-left"
