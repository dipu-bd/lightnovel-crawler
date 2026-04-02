# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class WuxiaSiteCrawler(WordpressTemplate):
    base_url = 'https://wuxiaworld.site/'
    chapter_body_selector = ".text-left"
