# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class PandaMangaxyzCrawler(MangaStreamTemplate):
    base_url = ["https://www.pandamanga.xyz/"]
