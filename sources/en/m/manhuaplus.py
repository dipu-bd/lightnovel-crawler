# -*- coding: utf-8 -*-

import logging
from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class ManhuplusOnline(MadaraTemplate):
    has_manga = True
    base_url = ["https://manhuaplus.online/"]