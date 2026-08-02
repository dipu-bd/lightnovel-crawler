# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.blogger import BloggerLabelTemplate

logger = logging.getLogger(__name__)


class NoiceTranslationsCrawler(BloggerLabelTemplate):
    base_url = ["https://noicetranslations.blogspot.com/"]

    can_search = True
