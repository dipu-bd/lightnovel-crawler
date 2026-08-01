# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class DuskBlossomsCrawler(MadaraTemplate):
    base_url = ["https://duskblossoms.com/"]
