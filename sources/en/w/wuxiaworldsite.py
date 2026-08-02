# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class WuxiaWorldSiteCrawler(MadaraTemplate):
    base_url = ["https://wuxiaworld.site/"]
