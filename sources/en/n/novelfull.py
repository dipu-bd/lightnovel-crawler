# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelFullCrawler(NovelFullTemplate):
    base_url = ["http://novelfull.com/", "https://novelfull.com/"]
    ajax_url = "ajax-chapter-option"
