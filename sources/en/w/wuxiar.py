import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaRCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiar.com/"
