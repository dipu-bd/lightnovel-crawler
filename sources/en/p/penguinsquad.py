# -*- coding: utf-8 -*-
import logging
import re
from typing import Dict, Optional, Tuple

from lncrawl.core import Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)

CHAPTER_NUMBER = re.compile(r"/chapter-(\d+)")


class PenguinSquadCrawler(SoupTemplate):
    base_url = ["https://penguin-squad.com/"]

    novel_title_selector = "h1"
    novel_cover_selector = "img[src*='/covers/']"
    novel_synopsis_selector = "p.line-clamp-3"
    novel_tags_selector = "span[class*='group/badge']"

    chapter_body_selector = ".reader-content"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # The publication status is a badge of the same shape as the genres.
        status = {"ongoing", "completed", "hiatus", "dropped"}
        novel.tags = [
            text
            for text in (
                tag.get_text(" ", strip=True) for tag in soup.select(self.novel_tags_selector)
            )
            if text and text.lower() not in status
        ]

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        rows = self._listed_chapters(soup)
        if not rows:
            return

        self._walk_hidden_chapters(rows)
        for number in sorted(rows):
            title, url = rows[number]
            novel.add_chapter(title=title, url=url)

    def _listed_chapters(self, soup: PageSoup) -> Dict[int, Tuple[str, str]]:
        rows: Dict[int, Tuple[str, str]] = {}
        for anchor in soup.select("div.divide-y > a[href]"):
            href = str(anchor.get("href") or "")
            number = self._number(href)
            if number is None:
                continue
            # The row prints the number in its own span, so the anchor's whole text repeats
            # it and trails the publication date; the paragraph holds the title alone.
            label = anchor.select_one("p")
            title = (label or anchor).get_text(" ", strip=True)
            rows[number] = (title, self.absolute_url(href))
        return rows

    def _walk_hidden_chapters(self, rows: Dict[int, Tuple[str, str]]) -> None:
        # The novel page prints the first and last handful and hides the rest behind a
        # "Show N more" button that fetches on click, so the middle has to be walked. Each
        # chapter page links to its neighbours, and the slug carries the number — which is
        # what tells next from previous, since the two links are identical but for the href.
        known = sorted(rows)
        gap = next(
            ((a, b) for a, b in zip(known, known[1:]) if b != a + 1),
            None,
        )
        if not gap:
            return

        start, end = gap
        number, url = start, rows[start][1]
        budget = end - start + 10
        while number < end and budget > 0:
            budget -= 1
            soup = self.scraper.get_soup(url)
            if number not in rows:
                # This page is the chapter's own, so its heading is the title to keep.
                heading = soup.select_one("h1")
                title = heading.get_text(" ", strip=True) if heading else f"Chapter {number}"
                rows[number] = (title, url)
            step = self._next_chapter(soup, number)
            if not step:
                break
            number, url = step

    def _next_chapter(self, soup: PageSoup, current: int) -> Optional[Tuple[int, str]]:
        for anchor in soup.select('a[href*="/chapter-"]'):
            href = str(anchor.get("href") or "")
            number = self._number(href)
            if number is not None and number > current:
                return number, self.absolute_url(href)
        return None

    def _number(self, href: str) -> Optional[int]:
        match = CHAPTER_NUMBER.search(href)
        return int(match.group(1)) if match else None
