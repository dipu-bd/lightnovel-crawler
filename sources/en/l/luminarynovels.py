import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class Luminarynovels(MadaraTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://luminarynovels.com/"]

    def initialize(self) -> None:
        # contains self-promo and discord link
        self.cleaner.bad_css.add("div.chapter-warning.alert.alert-warning")
