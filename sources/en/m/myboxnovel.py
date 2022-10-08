# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class MyBoxNovelCrawler(MadaraTemplate):
    base_url = ["https://myboxnovel.com/"]

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
        # self.cleaner.bad_tag_text_pairs.update(
        #     {
        #         "div": r"Visit our comic site Webnovel\.live",
        #     }
        # )
