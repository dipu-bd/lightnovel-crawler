# -*- coding: utf-8 -*-
import html
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

from lncrawl.core import Novel, PageSoup, SearchResult, SoupTemplate, Volume

logger = logging.getLogger(__name__)

NOVEL_PATH = re.compile(r"/novela-ligera/([^/?#]+)")
CHAPTER_NUMBER = re.compile(r"cap[ií]tulo[\s\-]*(\d+)", re.I)
PER_PAGE = 100


class NovelaEnEspanolCrawler(SoupTemplate):
    base_url = ["https://novelaenespanol.com/"]
    language = "es"

    can_search = True

    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        self._category: Dict[str, Any] = {}

    def _api(self, path: str) -> Any:
        return self.scraper.get_json(f"{self.scraper.origin}wp-json/wp/v2/{path}")

    def _novel_categories(self, query: str) -> List[Dict[str, Any]]:
        rows = self._api(
            f"categories?search={query}&per_page=20&_fields=id,name,slug,count,parent,link"
        )
        return [r for r in rows if not r.get("parent") and r.get("count")]

    def search(self, query: str) -> Iterable[SearchResult]:
        for row in self._novel_categories(query):
            yield SearchResult(
                title=html.unescape(str(row.get("name") or "")),
                url=str(row.get("link") or ""),
                info=f"{row.get('count')} capítulos",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        found = NOVEL_PATH.search(self.absolute_url(novel.url))
        if not found:
            raise ValueError(f"Not a novel url: {novel.url}")
        rows = self._api(
            f"categories?slug={found.group(1)}&_fields=id,name,slug,count,description"
        )
        if not rows:
            raise ValueError(f"No novel found for {novel.url}")
        self._category = rows[0]
        return self.scraper.get_soup(novel.url)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        novel.title = html.unescape(str(self._category.get("name") or ""))

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

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        description = str(self._category.get("description") or "")
        novel.synopsis = self.cleaner.clean_text(self.scraper.make_soup(description).text)

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows: List[Dict[str, Any]] = []
        page = 1
        while True:
            response = self.scraper.get(
                f"{self.scraper.origin}wp-json/wp/v2/posts"
                f"?categories={self._category['id']}&per_page={PER_PAGE}&page={page}"
                "&orderby=date&order=asc&_fields=link,title,date"
            )
            rows.extend(response.json())
            total = int(response.headers.get("X-WP-TotalPages") or 1)
            if page >= total:
                break
            page += 1

        chapters = []
        for row in rows:
            title = html.unescape(str(row.get("title", {}).get("rendered") or "")).strip()
            found = CHAPTER_NUMBER.search(title)
            if found:
                chapters.append((int(found.group(1)), str(row.get("date") or ""), title, row))

        # Every category carries one post that is the novel's own landing page rather than a
        # chapter, and it is the only one without a number in its title — measured against
        # the count the site prints, which is the post count minus exactly one.
        dropped = len(rows) - len(chapters)
        if dropped != 1:
            logger.warning("Dropped %d non-chapter posts from %s", dropped, novel.url)

        chapters.sort(key=lambda row: (row[0], row[1]))
        prefix = str(self._category.get("name") or "").strip()
        return [self._anchor(tag, row, prefix) for row in chapters]

    def _anchor(self, soup: PageSoup, row: tuple, prefix: str) -> PageSoup:
        title = row[2]
        if prefix and title.lower().startswith(prefix.lower()):
            title = title[len(prefix) :].strip(" -–:")
        return soup.new_tag("a", attrs={"href": str(row[3].get("link"))}, string=title)
