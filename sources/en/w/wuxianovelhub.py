import logging

from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class WuxiaNHCrawler(NovelMTLTemplate):
    base_url = "https://www.wuxianovelhub.com/"
