import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaHubCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiahub.com"
