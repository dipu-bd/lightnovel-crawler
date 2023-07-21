import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class ReadWNCrawler(NovelMTLTemplate):
    has_mtl = True
    base_url = [
        "https://www.readwn.com/",
        "https://www.wuxiap.com/"
    ]
