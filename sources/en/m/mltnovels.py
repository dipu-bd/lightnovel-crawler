# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class MltNovelsCrawler(MangaStreamTemplate):
    base_url = ["https://mltnovels.com/"]
    has_mtl = True
