# -*- coding: utf-8 -*-
import logging

from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelFullPlus(NovelFullTemplate):
    base_url = ["https://novelfullplus.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h1", "h2", "h3", "h4"])
