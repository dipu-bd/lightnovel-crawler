import logging
import re
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote

from ..core import Novel, PageSoup, SearchResult, SoupTemplate, Volume

logger = logging.getLogger(__name__)

LABEL_PATH = re.compile(r"/search/label/([^/?#&]+)")
CHAPTER_SPLIT = re.compile(r"\s+[-–—]\s+")
CHAPTER_LEAD = re.compile(r"^\s*(?:chapter|ch\.?|episode|ep\.?|part|vol)\b", re.I)


class BloggerLabelTemplate(SoupTemplate):
    """Blogger-hosted translation sites where a novel is a label and a chapter is a post.

    Blogger renders a handful of posts per page behind an "older posts" link, so scraping
    the archive means walking it blind. The JSON feed avoids that: it reports
    ``openSearch$totalResults`` up front, so the walk has a known length instead of ending
    when a page happens to look empty.

    Posts come back newest first, which is the reverse of reading order, and a blog serves
    fewer entries than asked for whenever its own cap is lower — so the walk advances by
    what actually arrived rather than by the page size it requested. Both are handled here,
    leaving a subclass only the base url.
    """

    is_template = True

    # Blogger answers the first feed call of a burst and challenges the ones behind it, with
    # a Google challenge no Cloudflare-shaped solver can clear. One request a second keeps
    # it answering; the feed is cheap enough that this costs a novel two calls.
    request_rate_limit = 1

    # The summary feed carries everything the list needs. Asking for `default` pulls the
    # full body of every post as well, which is a much larger response for no gain.
    feed_path = "feeds/posts/summary"
    page_size = 500

    # A blog usually carries a few housekeeping labels beside its novels ("Chapter",
    # "Project", "Announcement"), which are not novels and should not be offered as such.
    non_novel_labels: Iterable[str] = (
        "chapter",
        "chapters",
        "project",
        "projects",
        "announcement",
        "announcements",
        "news",
        "update",
        "updates",
        "release",
        "releases",
    )

    chapter_body_selector = ".post-body"

    _label: str = ""

    def _feed(self, path: str, **params: Any) -> Dict[str, Any]:
        query = "&".join(f"{k}={v}" for k, v in params.items())
        data = self.scraper.get_json(f"{self.scraper.origin}{path}?alt=json&{query}")
        return data.get("feed") or {}

    def novel_label(self, url: str) -> str:
        found = LABEL_PATH.search(url)
        if not found:
            raise ValueError(f"Not a novel url: {url}")
        return found.group(1)

    def is_novel_label(self, label: str) -> bool:
        return label.strip().lower() not in set(self.non_novel_labels)

    def search(self, query: str) -> Iterable[SearchResult]:
        feed = self._feed(self.feed_path, **{"max-results": 0})
        needle = query.strip().lower()
        for row in feed.get("category") or []:
            label = str(row.get("term") or "")
            if not label or not self.is_novel_label(label) or needle not in label.lower():
                continue
            yield SearchResult(
                title=label,
                url=f"{self.scraper.origin}search/label/{quote(label)}",
            )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        self._label = self.novel_label(self.absolute_url(novel.url))
        return self.scraper.get_soup(novel.url)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        from urllib.parse import unquote

        novel.title = unquote(self._label).replace("+", " ").strip()

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        entries = self.fetch_label_entries(self._label)
        anchors = []
        for entry in reversed(entries):  # the feed answers newest first
            link = self.entry_link(entry)
            title = str((entry.get("title") or {}).get("$t") or "").strip()
            if not link or not self.is_chapter_entry(entry, title):
                continue
            anchors.append(tag.new_tag("a", attrs={"href": link}, string=self.chapter_title(title)))
        return anchors

    def fetch_label_entries(self, label: str) -> List[Dict[str, Any]]:
        path = f"{self.feed_path}/-/{label}"
        entries: List[Dict[str, Any]] = []
        start = 1
        while True:
            feed = self._feed(path, **{"max-results": self.page_size, "start-index": start})
            batch = feed.get("entry") or []
            entries.extend(batch)
            total = int((feed.get("openSearch$totalResults") or {}).get("$t") or 0)
            if not batch or len(entries) >= total:
                break
            start += len(batch)
        return entries

    def entry_link(self, entry: Dict[str, Any]) -> str:
        for link in entry.get("link") or []:
            if link.get("rel") == "alternate" and link.get("href"):
                return str(link["href"])
        return ""

    def is_chapter_entry(self, entry: Dict[str, Any], title: str) -> bool:
        """Decide whether a post under the label is a chapter. Override to exclude more."""
        return True

    def chapter_title(self, title: str) -> str:
        """Drop the novel name these blogs prefix onto every post title.

        Matching it against the label is not enough — the same blog writes "I Became a
        Rich..." in the label and "I Became the Rich..." in half the titles. What is stable
        is the separator, so the tail is taken whenever it announces itself as a chapter.
        """
        parts = CHAPTER_SPLIT.split(title, maxsplit=1)
        if len(parts) == 2 and CHAPTER_LEAD.match(parts[1]):
            return parts[1].strip()
        return title

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        # Blogger's stock template emits an empty `keywords` meta, which the inherited
        # default turns into one blank tag.
        tag = soup.select_one(self.novel_tags_selector)
        raw = str(tag.get("content") or tag.text) if tag else ""
        novel.tags = [t.strip() for t in raw.split(",") if t.strip()]
