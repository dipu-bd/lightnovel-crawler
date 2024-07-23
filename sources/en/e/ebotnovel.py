import logging

from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)


class Ebotnovel(MangaStreamTemplate):
    has_mtl = True
    has_manga = False
    base_url = ["https://ebotnovel.com/"]
