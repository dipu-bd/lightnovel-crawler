# -*- coding: utf-8 -*-

import logging
from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class MangaStic(MadaraTemplate):
    has_manga = True
    base_url = ["https://mangastic.me/"]