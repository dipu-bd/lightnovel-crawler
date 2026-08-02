import html
import logging
import re
from typing import Any, Dict, Iterable, List, Optional

from ..core import Novel, PageSoup, SearchResult, SoupTemplate, Volume

logger = logging.getLogger(__name__)

_STRAIGHTEN = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})


class WpCategoryTemplate(SoupTemplate):
    """WordPress sites where a novel is a category and each chapter is a post in it.

    These themes render only a page or two of the newest chapters and often offer no pager
    at all, so the list comes from the REST feed instead. The feed reports its own page
    count in ``X-WP-TotalPages``, which means the walk has a known length rather than
    stopping when a page looks empty — the way a partial list gets mistaken for a whole one.

    Ordering is publication date. Chapter numbers are deliberately not used: sites running
    this shape bundle chapters into one post ("Chapter 01 - 05"), number by volume
    ("Volumen 1. Capítulo 1.1."), and carry the occasional six-digit typo, so any ordering
    derived from the numbers is worse than the one the site already has.
    """

    is_template = True

    api_root = "wp-json/wp/v2"
    novel_url_pattern = r"/category/([^/?#]+)"
    posts_per_page = 100

    # Kept narrow because these feeds are walked a hundred posts at a time and the full
    # rendered body of each is tens of kilobytes. Add a field where one is needed to decide
    # whether a post is a chapter, such as `content.protected`.
    post_fields = "link,title"

    # Several of these themes link the novel's own info post as a "read" button. That post
    # sits in the category but is not a chapter, and its position in the feed varies, so the
    # site naming it is the only reliable way to leave it out.
    landing_link_selector = "a.btn[href]"

    _category: Dict[str, Any] = {}

    def _api(self, path: str) -> Any:
        return self.scraper.get_json(f"{self.scraper.origin}{self.api_root}/{path}")

    def novel_slug(self, url: str) -> str:
        found = re.search(self.novel_url_pattern, url)
        if not found:
            raise ValueError(f"Not a novel url: {url}")
        return found.group(1)

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}{self.api_root}/categories?search={query}&per_page=20"

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
                info=f"{row.get('count')} chapters",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        slug = self.novel_slug(self.absolute_url(novel.url))
        rows = self._api(f"categories?slug={slug}&_fields=id,name,slug,count,description")
        if not rows:
            raise ValueError(f"No novel found for {novel.url}")
        self._category = rows[0]
        return self.scraper.get_soup(novel.url)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        novel.title = html.unescape(str(self._category.get("name") or ""))

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        description = str(self._category.get("description") or "")
        if description:
            novel.synopsis = self.cleaner.clean_text(self.scraper.make_soup(description).text)

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # An empty `keywords` meta is common on these themes, and the inherited default
        # turns it into a single blank tag.
        tags = soup.select_one(self.novel_tags_selector)
        raw = str(tags.get("content") or tags.text) if tags else ""
        novel.tags = [t.strip() for t in raw.split(",") if t.strip()]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        rows = self.fetch_chapter_posts()
        skip = self.landing_url(tag)
        prefix = str(self._category.get("name") or "").strip()

        anchors = []
        for row in rows:
            link = str(row.get("link") or "")
            if skip and link.rstrip("/") == skip:
                continue
            if not self.is_chapter_post(row):
                continue
            title = html.unescape(str(row.get("title", {}).get("rendered") or "")).strip()
            anchors.append(
                tag.new_tag("a", attrs={"href": link}, string=self.chapter_title(title, prefix))
            )
        return anchors

    def fetch_chapter_posts(self) -> List[Dict[str, Any]]:
        rows: List[Dict[str, Any]] = []
        page = 1
        while True:
            response = self.scraper.get(
                f"{self.scraper.origin}{self.api_root}/posts"
                f"?categories={self._category['id']}&per_page={self.posts_per_page}&page={page}"
                f"&orderby=date&order=asc&_fields={self.post_fields}"
            )
            rows.extend(response.json())
            total = int(response.headers.get("X-WP-TotalPages") or 1)
            if page >= total:
                break
            page += 1
        return rows

    def landing_url(self, soup: PageSoup) -> str:
        if not self.landing_link_selector:
            return ""
        tag = soup.select_one(self.landing_link_selector)
        return self.absolute_url(str(tag.get("href"))).rstrip("/") if tag else ""

    def is_chapter_post(self, row: Dict[str, Any]) -> bool:
        """Decide whether a post in the category is a chapter. Override to exclude more."""
        return True

    def chapter_title(self, title: str, prefix: str) -> str:
        """Drop the novel's name, which these themes repeat in every chapter title."""
        if not prefix:
            return title
        # A title often curls the quotes its category name leaves straight, so the two
        # spellings have to be flattened before they can be compared.
        flat = title.translate(_STRAIGHTEN).lower()
        if not flat.startswith(prefix.translate(_STRAIGHTEN).lower()):
            return title
        rest = title[len(prefix) :].strip(" -–—:.")
        # A title of "Off Guard 278" reduces to "278", which reads as nothing at all in a
        # chapter list. Where the name is all that makes the number a chapter, keep it.
        if not rest or rest.isdigit():
            return title
        return rest
