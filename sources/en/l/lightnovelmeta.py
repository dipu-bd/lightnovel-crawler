import logging

from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class LightNovelMetaCrawler(NovelMTLTemplate):
    base_url = "https://www.lightnovelmeta.com"
