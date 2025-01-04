# -*- coding: utf-8 -*-
import logging

from sources.en.a.asianovel_net import AsiaNovelNetCrawler

logger = logging.getLogger(__name__)


class WuxiaSkyCrawler(AsiaNovelNetCrawler):
    base_url = ["https://www.wuxiasky.net"]
