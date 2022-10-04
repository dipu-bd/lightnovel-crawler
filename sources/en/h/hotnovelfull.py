# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class HotNovelFullCrawler(NovelFullTemplate):
    base_url = ["https://hotnovelfull.com/"]
