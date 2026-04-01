# -*- coding: utf-8 -*-
from lncrawl.core import BrowserTemplate


class NovelsOnline(BrowserTemplate):
    base_url = ["https://novelsonline.net/"]
    has_manga = False
    has_mtl = False

    novel_title_selector = ".block-title h1"
    novel_cover_selector = "img[alt*='Cover']"
    novel_author_selector = "a[href*=author]"
    chapter_list_selector = ".chapters .chapter-chs li a[href]"
    chapter_body_selector = "#contentall"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["div"])
        self.cleaner.bad_css.update(
            [
                ".trinity-player-iframe-wrapper",
                ".hidden",
                ".ads-title",
                "script",
                "center",
                "interaction",
                "a[href*=remove-ads]",
                "a[target=_blank]",
                "hr",
                "br",
                "#growfoodsmart",
                ".col-md-6",
                ".trv_player_container",
                ".ad1",
            ]
        )
