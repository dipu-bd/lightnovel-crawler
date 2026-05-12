# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.exceptions import LNException
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelbinCrawler(NovelFullTemplate):
    base_url = ["https://novelbin.com/"]

    def initialize(self) -> None:
        self.taskman.init_executor(ratelimit=0.99)

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        nl_id = tag.select_one("#rating[data-novel-id]")["data-novel-id"]
        if not nl_id:
            raise LNException("No novel_id found")
        url = f"{self.scraper.origin}ajax/chapter-option?novelId={nl_id}"
        soup = self.scraper.get_soup(url)
        return soup.select("select > option[value]")
