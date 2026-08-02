# -*- coding: utf-8 -*-
import html
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

from lncrawl.core import Novel, PageSoup, SearchResult, SoupTemplate, Volume

logger = logging.getLogger(__name__)

TAG_PATH = re.compile(r"/tag/([^/?#]+)")
TITLE_PREFIX = re.compile(r"^\s*novel\s*[:\-–]?\s*", re.I)
PER_PAGE = 100


class XperimentalHamidCrawler(SoupTemplate):
    """A general-interest blog that also publishes novels, one chapter per post.

    Nothing groups a novel except its tag — the categories are genres, and the novel page a
    reader would expect does not exist. So a novel is a tag archive, and the chapter list is
    the tag's REST feed.
    """

    base_url = ["https://xperimentalhamid.com/"]

    can_search = True

    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        self._tag: Dict[str, Any] = {}

    def _api(self, path: str) -> Any:
        return self.scraper.get_json(f"{self.scraper.origin}wp-json/wp/v2/{path}")

    def search(self, query: str) -> Iterable[SearchResult]:
        rows = self._api(f"tags?search={query}&per_page=30&_fields=id,name,slug,count,link")
        # Each novel carries half a dozen near-duplicate tags built by appending "pdf",
        # "full", "read-online" and the like to the real one, and they all hold roughly the
        # same posts. Matching on the slug alone would also drop a genuine novel whose name
        # extends another's, so the count has to agree before one is called a duplicate.
        counts = {str(r.get("slug") or ""): int(r.get("count") or 0) for r in rows}
        for row in sorted(rows, key=lambda r: -int(r.get("count") or 0)):
            slug = str(row.get("slug") or "")
            count = int(row.get("count") or 0)
            if not count:
                continue
            if any(
                slug.startswith(f"{other}-") and abs(count - other_count) <= max(2, count // 20)
                for other, other_count in counts.items()
                if other != slug
            ):
                continue
            yield SearchResult(
                title=html.unescape(str(row.get("name") or "")),
                url=str(row.get("link") or ""),
                info=f"{row.get('count')} posts",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        found = TAG_PATH.search(self.absolute_url(novel.url))
        if not found:
            raise ValueError(f"Not a novel url: {novel.url}")
        rows = self._api(f"tags?slug={found.group(1)}&_fields=id,name,slug,count")
        if not rows:
            raise ValueError(f"No novel found for {novel.url}")
        self._tag = rows[0]
        return self.scraper.get_soup(novel.url)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        novel.title = html.unescape(str(self._tag.get("name") or ""))

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # Only the genres under /topics/novels/ say anything about the novel; the rest of
        # /topics/ is the blog's own nav — News, Tech, Finance and so on.
        novel.tags = [
            t
            for t in (a.text.strip() for a in soup.select("a[href*='/topics/novels/']"))
            if t and t.lower() != "novels"
        ]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows: List[Dict[str, Any]] = []
        page = 1
        while True:
            response = self.scraper.get(
                f"{self.scraper.origin}wp-json/wp/v2/posts"
                f"?tags={self._tag['id']}&per_page={PER_PAGE}&page={page}"
                "&orderby=date&order=asc&_fields=link,title"
            )
            rows.extend(response.json())
            total = int(response.headers.get("X-WP-TotalPages") or 1)
            if page >= total:
                break
            page += 1

        # The tag also holds the novel's own review post, which lives outside /novels/.
        # Numbering cannot be used to spot it: early posts cover five chapters each
        # ("Chapter 01 - 05"), so the numbers are sparse by design rather than incomplete.
        prefix = str(self._tag.get("name") or "").strip()
        anchors = []
        for row in rows:
            link = str(row.get("link") or "")
            if "/novels/" not in link:
                continue
            title = html.unescape(str(row.get("title", {}).get("rendered") or "")).strip()
            if prefix and title.lower().startswith(prefix.lower()):
                title = TITLE_PREFIX.sub("", title[len(prefix) :].strip(" -–:"))
            anchors.append(tag.new_tag("a", attrs={"href": link}, string=title))
        return anchors
