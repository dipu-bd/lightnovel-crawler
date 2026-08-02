import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class Novel_Bin(NovelFullTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://novel-bin.com/", "https://novelbin.me"]
    request_rate_limit = 1
    chapter_list_on_novel_page = True
