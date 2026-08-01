# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class TsundokuCrawler(MangaStreamTemplate):
    base_url = ["https://tsundoku.com.br/"]
    can_search = True
