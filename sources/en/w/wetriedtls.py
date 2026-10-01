# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, Iterable
from urllib.parse import urlencode

from lncrawl.core import Chapter, Novel, SearchResult, SoupTemplate
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)

API_URL = "https://api.wetriedtls.com"


class WeTriedTlsCrawler(SoupTemplate):
    base_url = ["https://wetriedtls.com/"]
    can_search = True

    def initialize(self) -> None:
        # Every chapter opens and closes with team credits and a Discord invite.
        self.cleaner.bad_tag_text_pairs.update(
            {
                "p": re.compile(
                    r"^\s*(WeTried Translations|Translator:|Editor:|Discord:|Join our discord)",
                    re.I,
                ),
            }
        )

    # HeanCMS: the pages are Next.js RSC payloads; the JSON API the front-end calls is cleaner.
    def _api(self, path: str, **params: Any) -> Any:
        url = f"{API_URL}/{path}"
        if params:
            url += f"?{urlencode(params)}"
        return self.scraper.get_json(url)

    def search(self, query: str) -> Iterable[SearchResult]:
        data = self._api(
            "query", query_string=query, series_type="Novel", adult="true", page=1, perPage=20
        )
        for series in data["data"]:
            yield SearchResult(
                title=series["title"],
                url=f"{self.scraper.origin}series/{series['series_slug']}",
                info=f"Status: {series.get('status')}",
            )

    def read_novel(self, novel: Novel) -> None:
        match = re.search(r"/series/([^/?#]+)", novel.url)
        if not match:
            raise LNException(f"Invalid novel URL: {novel.url}")
        slug = match.group(1)

        series = self._api(f"series/{slug}")
        novel.title = series["title"]
        novel.cover_url = self.absolute_url(series.get("thumbnail"), page_url=novel.url)
        novel.author = series.get("author") or ""
        novel.synopsis = series.get("description") or ""
        novel.tags = [t["name"] for t in series.get("tags") or []]

        # This endpoint lists free chapters only; paid ones come from `/chapters/{id}/paid`.
        data = self._api(f"chapters/{series['id']}", page=1, perPage=10000, query="", order="asc")
        if data["meta"]["last_page"] > 1:
            raise LNException(f"Chapter list truncated: {data['meta']['total']} chapters")

        novel.volumes = []
        novel.chapters = []
        for item in data["data"]:
            title = item["chapter_name"]
            if item.get("chapter_title"):
                title += f": {item['chapter_title']}"
            novel.add_chapter(
                title=title,
                url=f"{self.scraper.origin}series/{slug}/{item['chapter_slug']}",
            )

    def download_chapter(self, chapter: Chapter) -> None:
        match = re.search(r"/series/([^/?#]+)/([^/?#]+)", chapter.url)
        if not match:
            raise LNException(f"Invalid chapter URL: {chapter.url}")
        data = self._api(f"chapter/{match.group(1)}/{match.group(2)}")
        content = (data.get("chapter") or {}).get("chapter_content")
        if data.get("paywall") or not content:
            raise LNException(f"Chapter is paywalled or empty: {chapter.url}")
        soup = self.scraper.make_soup(content)
        chapter.body = self.cleaner.extract_contents(soup.select_one("body"))
