import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Novel_Bin(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://novel-bin.com/"]
