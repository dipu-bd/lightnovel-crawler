# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict

from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)

SYNOPSIS_PATH = "/synopsis/"


class CangJiCrawler(WpCategoryTemplate):
    base_url = ["https://cangji.net/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    # No "read" button here, and the info pages live in their own category rather than
    # inside each novel's.
    landing_link_selector = ""

    post_fields = "link,title,content.protected"

    def is_chapter_post(self, row: Dict[str, Any]) -> bool:
        # Most of this site's back catalogue is behind a post password for supporters, and
        # a locked page still answers 200 with an empty body. Listing those would hand the
        # reader a run of blank chapters, so only the free ones are offered.
        if (row.get("content") or {}).get("protected"):
            return False
        return SYNOPSIS_PATH not in str(row.get("link") or "")

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(".entry-content img[src], article img[src]")
        if tag:
            novel.cover_url = self.absolute_url(str(tag.get("src")))
