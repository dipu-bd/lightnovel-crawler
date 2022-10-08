# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Hs2ppeCrawler(NovelFullTemplate):
    base_url = ["http://hs2ppe.co.uk/"]
