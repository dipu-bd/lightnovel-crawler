# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ZinNovelCrawler(WordpressTemplate):
    base_url = "https://zinnovel.com/"
    madara_body_from_paragraphs = True
