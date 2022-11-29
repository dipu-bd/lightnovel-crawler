import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Novelbin_Net(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://novelbin.net/"]
