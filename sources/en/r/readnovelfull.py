# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class ReadNovelFullCrawler(NovelFullTemplate):
    base_url = "https://readnovelfull.com/"
