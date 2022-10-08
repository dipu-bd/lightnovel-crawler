# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class AllNovelFullCrawler(NovelFullTemplate):
    base_url = ["https://allnovelfull.com/"]
