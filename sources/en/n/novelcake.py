# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelCakeCrawler(WordpressTemplate):
    base_url = 'https://novelcake.com/'
    madara_body_from_paragraphs = True
