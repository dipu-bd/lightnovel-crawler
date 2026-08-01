# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class HyacinthBloomCrawler(MangaStreamTemplate):
    base_url = ["https://hyacinthbloom.com/"]
    can_search = True
