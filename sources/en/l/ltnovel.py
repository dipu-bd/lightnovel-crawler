import logging
from lncrawl.templates.novelmtl import NovelMTLTemplate

logger = logging.getLogger(__name__)


class LtNovel(NovelMTLTemplate):
    base_url = "https://www.ltnovel.com/"
