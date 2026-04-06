# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class LightNovelsHubCrawler(WordpressTemplate):
    base_url = "https://lightnovelshub.com/"
    madara_body_from_paragraphs = True
