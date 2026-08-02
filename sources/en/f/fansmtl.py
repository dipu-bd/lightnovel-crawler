# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class FansMtlCrawler(NovelMTLTemplate):
    base_url = ["https://www.fansmtl.com/"]
