# -*- coding: utf-8 -*-
import re
from typing import Iterable, Optional

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

CHAPTER_PATH = re.compile(r"^/b/\d+/c/(\d+)$")


class XszjCrawler(SoupTemplate):
    """Crawler for 小说之家 (xszj.org)."""

    base_url = ["https://xszj.org/"]
    language = "zh"
    request_rate_limit = 0.5

    novel_title_selector = 'meta[property="og:novel:book_name"]'
    novel_cover_selector = 'meta[property="og:image"]'
    novel_author_selector = 'meta[property="og:novel:author"]'
    novel_synopsis_selector = "#intro"
    chapter_body_selector = "#booktxt"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_title_selector)
        novel.title = str(tag.get("content") or "").strip()

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_author_selector)
        novel.author = str(tag.get("content") or "").strip()

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one('meta[property="og:novel:category"]')
        category = str(tag.get("content") or "").strip() if tag else ""
        novel.tags = [category] if category else []

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        # The newest handful are repeated above the complete table of contents.
        chapters: dict[int, PageSoup] = {}
        for anchor in tag.select('#list a[rel="chapter"][href]'):
            match = CHAPTER_PATH.match(str(anchor.get("href") or ""))
            if match:
                chapters[int(match.group(1))] = anchor
        return [chapters[key] for key in sorted(chapters)]

    def download_chapter(self, chapter: Chapter) -> None:
        # Long chapters are split across ?page=2, ?page=3, ... pages. Follow only
        # links labelled 下一页 so that the next chapter is not merged into this one.
        url = self.build_chapter_url(chapter)
        seen: set[str] = set()
        pages: list[str] = []

        while url not in seen:
            seen.add(url)
            soup = self.scraper.get_soup(url)
            body = soup.select_one(self.chapter_body_selector)
            if not body:
                raise RuntimeError(f"Chapter body not found: {url}")

            pages.append(self.cleaner.extract_contents(body))
            next_page = next(
                (
                    anchor
                    for anchor in soup.select(".bottem1 a[href]")
                    if anchor.get_text(strip=True) == "下一页"
                ),
                None,
            )
            if next_page is None:
                break
            url = self.absolute_url(str(next_page.get("href")))

        chapter.body = "\n".join(pages)
