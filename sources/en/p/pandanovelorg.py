import logging
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Pandanovelorg(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://pandanovel.org/"]
