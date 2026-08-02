# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class NovellatteCrawler(BloggerLabelTemplate):
    base_url = ["https://novellatte.blogspot.com/"]

    can_search = True
