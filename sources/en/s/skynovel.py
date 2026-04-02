# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class SkyNovel(WordpressTemplate):
    base_url = 'https://skynovel.org/'
    madara_body_from_paragraphs = True
