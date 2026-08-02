# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class LadasBlMtlCrawler(BloggerLabelTemplate):
    base_url = ["https://ladasblmtl.blogspot.com/"]

    can_search = True

    # This blog tags every post with its genre as well as its novel, and the genre labels are
    # the two biggest — offered as novels they would each look like a 197-chapter book.
    non_novel_labels = tuple(BloggerLabelTemplate.non_novel_labels) + ("bl", "danmei")
