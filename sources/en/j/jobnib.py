# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class JobnibCrawler(MangaStreamTemplate):
    base_url = ["https://jobnib.com/"]
