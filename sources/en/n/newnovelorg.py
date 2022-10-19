import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class NewNovelOrg(MadaraTemplate):
    has_mtl = False
    has_manga = False
    base_url = ["https://newnovel.org/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".para-comment",
                ".j_open_para_comment",
                ".j_para_comment_count",
                ".para-comment-num",
                "#wp-manga-current-chap",
                ".cha-tit",
                ".subtitle ",
            ]
        )
