# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class MixedNovelNet(WordpressTemplate):
    base_url = ['https://mixednovel.net/', 'https://earlynovel.net/']
    chapter_body_selector = ".reading-content .text-left"

    def initialize(self) -> None:
        self.taskman.init_executor(1)
