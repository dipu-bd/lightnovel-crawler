import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class NovelMtCrawler(NovelMTLTemplate):
    has_mtl = True
    base_url = "https://www.novelmt.com/"
