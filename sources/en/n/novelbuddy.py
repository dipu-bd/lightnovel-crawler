# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, Iterable
from urllib.parse import urlparse

from lncrawl.core import Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)

API_URL = "https://api.novelbuddy.me"


class NovelbuddyCrawler(SoupTemplate):
    base_url = [
        "https://novelbuddy.me/",
        "https://novelbuddy.io/",
        "https://novelbuddy.com/",
    ]

    has_mtl = True
    can_search = True

    chapter_body_selector = "article"

    def initialize(self) -> None:
        self.title_data: Dict[str, Any] = {}

    def search(self, query: str) -> Iterable[SearchResult]:
        data = self.scraper.get_json(f"{API_URL}/titles/search", params={"q": query})
        for item in (data.get("data") or {}).get("items") or []:
            yield SearchResult(
                title=item.get("name") or "",
                url=self.absolute_url(item.get("url") or ""),
                info=item.get("status") or "",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        # Only the newest fifty chapters are ever rendered, and a novel with no genre or
        # author links falls through to the site-wide meta tags, which name NovelBuddy
        # itself and a list of SEO keywords. The API answers both properly, so the page is
        # fetched for the chapter text alone.
        slug = urlparse(self.absolute_url(novel.url)).path.strip("/").split("/")[0]
        lookup = self.scraper.get_json(f"{API_URL}/titles/by-slug/{slug}")
        title_id = lookup["data"]["new_url"].rsplit("/", 1)[-1].split("-", 1)[0]
        detail = self.scraper.get_json(f"{API_URL}/titles/{title_id}")
        self.title_data = (detail.get("data") or {}).get("title") or {}
        self.title_data["id"] = title_id
        return self.scraper.get_soup(self.build_novel_url(novel))

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        novel.title = self.title_data.get("name") or ""

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        cover = self.title_data.get("cover")
        if cover:
            novel.cover_url = self.absolute_url(cover)

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        names = [a.get("name") for a in self.title_data.get("authors") or []]
        novel.author = ", ".join(name for name in names if name)

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = [
            genre["name"] for genre in self.title_data.get("genres") or [] if genre.get("name")
        ]

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        novel.synopsis = self.cleaner.extract_contents(
            PageSoup.create(self.title_data.get("summary") or "")
        )

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        chapters = self.scraper.get_json(f"{API_URL}/titles/{self.title_data['id']}/chapters")
        for item in reversed((chapters.get("data") or {}).get("chapters") or []):
            novel.add_chapter(
                title=item.get("name") or "",
                url=self.absolute_url(item.get("url") or ""),
            )
