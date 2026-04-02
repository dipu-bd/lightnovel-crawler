# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ListNovelCrawler(WordpressTemplate):
    base_url = 'https://listnovel.com/'
    madara_body_from_paragraphs = True
