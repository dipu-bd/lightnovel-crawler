# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelFullPlus(NovelFullTemplate):
    base_url = ["https://novelfullplus.com/"]
