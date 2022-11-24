# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class SystemTranslationCrawler(MangaStreamTemplate):
    base_url = ["https://systemtranslation.com/"]
