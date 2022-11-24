# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class ImperfectComicCrawler(MangaStreamTemplate):
    base_url = ["https://imperfectcomic.org/"]
    has_manga = True
