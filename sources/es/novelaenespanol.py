# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Novel, PageSoup
from lncrawl.templates.wpcategory import WpCategoryTemplate

logger = logging.getLogger(__name__)


class NovelaEnEspanolCrawler(WpCategoryTemplate):
    base_url = ["https://novelaenespanol.com/"]
    language = "es"

    can_search = True

    chapter_body_selector = ".entry-content"

    novel_url_pattern = r"/novela-ligera/([^/?#]+)"

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(".arh-thumb img[src], article img[src], .entry-content img[src]")
        if tag:
            novel.cover_url = self.absolute_url(str(tag.get("src")))

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # The genre links share a prefix with the two status links, which are a listing
        # filter rather than something true of the novel.
        tags = []
        for anchor in soup.select("a[href*='/novelas-ligeras/']"):
            href = str(anchor.get("href") or "").rstrip("/")
            text = anchor.text.strip()
            if text and not href.endswith(("/completed", "/ongoing")):
                tags.append(text)
        novel.tags = tags
