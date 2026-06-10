# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.wordpress import WordpressTemplate

logger = logging.getLogger(__name__)


class NovelNiceCrawler(WordpressTemplate):
    base_url = "https://novelnice.com/"
    has_mtl = False
    has_manga = False
    madara_body_from_paragraphs = True
    novel_author_selector = '.author-content a[href*="novel-author"]'
    novel_tags_selector = '.genres-content a[href*="novel-genre"]'
