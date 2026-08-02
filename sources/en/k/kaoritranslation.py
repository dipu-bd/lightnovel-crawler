# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class KaoriTranslationCrawler(BloggerLabelTemplate):
    base_url = ["https://kaoritranslation.blogspot.com/"]

    can_search = True
