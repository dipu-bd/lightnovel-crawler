# -*- coding: utf-8 -*-

import logging
from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class BestMangaCrawler(MadaraTemplate):
    has_manga = True
    base_url = ["https://bestmanga.club/"]
