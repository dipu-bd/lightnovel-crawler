import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaPubCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxiapub.com/"
