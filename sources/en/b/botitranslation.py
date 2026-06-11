# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional, Union

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume, BrowserTemplate

logger = logging.getLogger(__name__)


class BotiTranslationCrawler(SoupTemplate):
    base_url = "https://www.botitranslation.com/"

    novel_title_selector = ".info-section .book-name span"
    novel_author_selector = ".info-section .author-name"
    novel_cover_selector = ".cover img.cover-img[src]"

    chapter_body_selector = ".chapter-content"

    def parse_chapter_list(
        self, soup: PageSoup, novel: Novel
    ) -> Generator[Union[Chapter, Volume], None, None]:
        links = list(soup.select(".container div#toc-panel table tbody tr td a[href]"))
        for idx, a in enumerate(links, 0):
            yield Chapter(
                id=idx,
                title=a.get_text(strip=True),
                url=self.absolute_url(a["href"]),
            )
        logger.info("Found %d chapters", len(links))