import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaZCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiaz.com/"
