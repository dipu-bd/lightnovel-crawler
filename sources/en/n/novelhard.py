# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelHardCrawler(WordpressTemplate):
    base_url = 'https://novelhard.com/'
    chapter_body_selector = ".reading-content .text-left"
