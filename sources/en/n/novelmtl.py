import logging

from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class Novelmtl(NovelMTLTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://www.novelmtl.com/"]
