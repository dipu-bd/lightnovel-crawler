# -*- coding: utf-8 -*-
import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)

class ReadWNCrawler(NovelMTLTemplate):
    machine_translation = True
    base_url = 'https://www.readwn.com/'
