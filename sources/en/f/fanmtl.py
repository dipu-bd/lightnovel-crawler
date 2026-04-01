# -*- coding: utf-8 -*-
from lncrawl.templates.novelmtl import NovelMTLTemplate


class FanMTLCrawler(NovelMTLTemplate):
    has_mtl = True
    base_url = "https://www.fanmtl.com/"

    def initialize(self):
        super().initialize()
        self.cleaner.bad_css.update(
            {
                'div[align="center"]',
            }
        )
