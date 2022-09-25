import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class NovelMtCrawler(NovelMTLTemplate):
    machine_translation = True
    base_url = "https://www.novelmt.com/"
