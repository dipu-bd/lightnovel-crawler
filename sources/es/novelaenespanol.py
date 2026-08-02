# -*- coding: utf-8 -*-
import html
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

from lncrawl.core import Novel, PageSoup, SearchResult, SoupTemplate, Volume

logger = logging.getLogger(__name__)

NOVEL_PATH = re.compile(r"/novela-ligera/([^/?#]+)")
PER_PAGE = 100


class NovelaEnEspanolCrawler(SoupTemplate):
    """Each novel is a WordPress category and each chapter an ordinary post in it.

    The theme renders only the thirty newest chapters and offers no pager, so the list is
    taken from the REST feed, which reports its own page count and is therefore walked to a
    known length rather than until something looks empty.
    """

    base_url = ["https://novelaenespanol.com/"]
    language = "es"

    can_search = True

    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        self._category: Dict[str, Any] = {}

    def _api(self, path: str) -> Any:
        return self.scraper.get_json(f"{self.scraper.origin}wp-json/wp/v2/{path}")

    def search(self, query: str) -> Iterable[SearchResult]:
        rows = self._api(
            f"categories?search={query}&per_page=20&_fields=id,name,slug,count,parent,link"
        )
        for row in rows:
            if row.get("parent") or not row.get("count"):
                continue
            yield SearchResult(
                title=html.unescape(str(row.get("name") or "")),
                url=str(row.get("link") or ""),
                info=f"{row.get('count')} capítulos",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        found = NOVEL_PATH.search(self.absolute_url(novel.url))
        if not found:
            raise ValueError(f"Not a novel url: {novel.url}")
        rows = self._api(f"categories?slug={found.group(1)}&_fields=id,name,slug,count,description")
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
        # Publication order is the only ordering this site supports. Chapter numbers are
        # not usable: one novel numbers nothing but its volumes ("Volumen 1. Capítulo
        # 1.1."), another carries a typo six digits long, and a third writes "Capítulos"
        # for a single chapter.
        rows: List[Dict[str, Any]] = []
        page = 1
        while True:
            response = self.scraper.get(
                f"{self.scraper.origin}wp-json/wp/v2/posts"
                f"?categories={self._category['id']}&per_page={PER_PAGE}&page={page}"
                "&orderby=date&order=asc&_fields=link,title"
            )
            rows.extend(response.json())
            total = int(response.headers.get("X-WP-TotalPages") or 1)
            if page >= total:
                break
            page += 1

        # Every category holds one post that is the novel's own info page. Its position in
        # the feed varies, and its title does not distinguish it — dropping posts whose
        # title lacks a chapter number instead cost seventeen real chapters of Martial Peak.
        # The novel page links it as the "read" button, so the site names it for us.
        landing = tag.select_one("a.btn[href]")
        skip = self.absolute_url(str(landing.get("href"))).rstrip("/") if landing else ""

        prefix = str(self._category.get("name") or "").strip()
        anchors = []
        for row in rows:
            link = str(row.get("link") or "")
            if skip and link.rstrip("/") == skip:
                continue
            title = html.unescape(str(row.get("title", {}).get("rendered") or "")).strip()
            if prefix and title.lower().startswith(prefix.lower()):
                title = title[len(prefix) :].strip(" -–:.")
            anchors.append(tag.new_tag("a", attrs={"href": link}, string=title))
        return anchors
