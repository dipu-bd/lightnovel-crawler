# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, PageSoup
from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)

PAYWALL = re.compile(r"premium content", re.I)


class HyacinthBloomCrawler(WpCategoryTemplate):
    base_url = ["https://hyacinthbloom.com/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    landing_link_selector = ""

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        # This site sells most of each novel. Off Guard opens at chapter 100 and serves a
        # "Premium Content" notice for all 179 after it, so the split is a standing paywall
        # rather than an early-access window that catches up. Saving the notice would record
        # a paid chapter as a fifty-character one; an empty body marks it unavailable, which
        # is what it is.
        #
        # The REST feed hands back the text of those chapters regardless of the paywall.
        # That is the site's mistake to fix, not a route to take.
        body = self.cleaner.extract_contents(soup)
        chapter.body = "" if PAYWALL.search(body) else body
