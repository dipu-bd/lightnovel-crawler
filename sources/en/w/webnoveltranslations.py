# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class WebNovelTranslationsCrawler(MadaraTemplate):
    base_url = ["https://webnoveltranslations.com/"]
