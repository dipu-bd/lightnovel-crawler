# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelupdates import NovelupdatesTemplate

logger = logging.getLogger(__name__)


class NovelupdatesCrawler(NovelupdatesTemplate):
    base_url = ["https://www.novelupdates.com/"]
