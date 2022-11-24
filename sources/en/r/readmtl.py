import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class Readmtl(MadaraTemplate):
    has_mtl = True
    has_manga = False
    base_url = ["https://readmtl.com/"]
