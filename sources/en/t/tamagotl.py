# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class TamagoTlCrawler(MangaStreamTemplate):
    base_url = ["https://tamagotl.com/"]
    has_mtl = True
