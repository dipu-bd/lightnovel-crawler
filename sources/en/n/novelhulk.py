# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelHulkCrawler(NovelFullTemplate):
    base_url = ["https://novelhulk.com/"]
