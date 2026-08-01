# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class TranslatinOtakuCrawler(MadaraTemplate):
    base_url = ["https://translatinotaku.net/"]
