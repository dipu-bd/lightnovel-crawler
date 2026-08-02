# -*- coding: utf-8 -*-
import logging

from lncrawl.core import SoupTemplate

logger = logging.getLogger(__name__)


class PeachPittingCrawler(SoupTemplate):
    base_url = ["https://peachpitting.com/"]

    # Both the site name and the novel name are h1 on a novel page; only the second is the
    # novel, and the theme also gives it a class of its own.
    novel_title_selector = ".page-title"

    # The chapter list is rendered by a content-views plugin rather than by the theme.
    chapter_list_selector = ".pt-cv-title a[href]"

    # `article` and `#primary` also hold the text, but each wraps it in the post header and
    # the comment thread; this is the prose on its own.
    chapter_body_selector = "#wtr-content"
