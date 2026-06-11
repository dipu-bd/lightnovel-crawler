# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.models import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class BotiTranslationCrawler(GeneralSoupTemplate):
    base_url = "https://www.botitranslation.com/"

    def parse_title(self, soup: BeautifulSoup) -> str:
        """Return the novel title from the novel page."""
        #raise NotImplementedError()  # e.g. return soup.select_one("h1.title").get_text(strip=True)
        return soup.select_one("div.book-name span").get_text()

    def parse_cover(self, soup: BeautifulSoup) -> Optional[str]:
        """Return the cover image URL, or '' if none."""

        #return ""

        return soup.select_one("div.cover img.cover-img").get_text()

    def parse_chapter_list(
        self, soup: BeautifulSoup
    ) -> Generator[Union[Chapter, Volume], None, None]:
        links = soup.select("tr td a")
        for idx, a in enumerate(links, 1):
            yield Chapter(
                id=idx,
                title=a.get_text(strip=True),
                url=self.absolute_url(a["href"]),
            )
        logger.info("Found %d chapters", len(links))

    def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        """Return the Tag that contains the chapter text (soup is the chapter page)."""

        return soup.select_one("div.chapter-content")

        #raise NotImplementedError()  # e.g. return soup.select_one(".chapter-content")