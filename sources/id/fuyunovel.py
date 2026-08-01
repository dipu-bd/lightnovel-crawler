# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class FuyuNovelCrawler(MangaStreamTemplate):
    base_url = ["https://fuyu-novel.my.id/"]
    can_search = True
