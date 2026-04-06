# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class NovelTranslateCrawler(WordpressTemplate):
    base_url = "https://noveltranslate.com/"
    madara_body_from_paragraphs = True
