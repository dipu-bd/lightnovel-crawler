# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class OtakuTranslationCrawler(BloggerLabelTemplate):
    base_url = ["https://otakutl.blogspot.com/"]

    can_search = True
