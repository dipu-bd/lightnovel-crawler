# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.madara import MadaraTemplate

logger = logging.getLogger(__name__)


class BoxNovelCrawler(MadaraTemplate):
    base_url = ["https://boxnovel.com/"]

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
        self.cleaner.bad_tag_text_pairs.update(
            {
                "p": r"Thank you for reading on myboxnovel.com"
            }
        )
