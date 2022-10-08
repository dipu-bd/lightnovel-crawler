import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaMTLCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiamtl.com"
    has_mtl = True
