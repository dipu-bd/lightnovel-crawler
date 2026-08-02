# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class LnMakineCeviriCrawler(BloggerLabelTemplate):
    base_url = ["https://lnmakineceviri.blogspot.com/"]
    language = "tr"

    can_search = True
