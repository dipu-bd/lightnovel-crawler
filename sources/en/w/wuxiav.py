import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaVCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiav.com/"
