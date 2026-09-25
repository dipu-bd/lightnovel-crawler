# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, Dict, Iterable
from urllib.parse import urlencode

from lncrawl.core import Chapter, Novel, SearchResult, SoupTemplate
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)

API_URL = "https://api.mystorywave.com/story-wave-backend/api/v1/content"


class BotiTranslationCrawler(SoupTemplate):
    base_url = [
        "https://www.botitranslation.com/",
        "https://botitranslation.com/",
    ]
    can_search = True

    # The pages are a JS shell behind Cloudflare; the StoryWave API the front-end calls is not.
    # It resolves books and search against the org named by `site-domain`.
    def _api(self, path: str, **params: Any) -> Any:
        url = f"{API_URL}/{path}"
        if params:
            url += f"?{urlencode(params)}"
        res = self.scraper.get_json(url, headers={"site-domain": "www.botitranslation.com"})
        if res.get("code") != 0:
            raise LNException(f"API error on {path}: {res.get('message')}")
        return res["data"]

    def search(self, query: str) -> Iterable[SearchResult]:
        data = self._api("books/search", keyWord=query, pageNumber=1, pageSize=20)
        for book in data["list"]:
            yield SearchResult(
                title=book["title"],
                url=f"{self.scraper.origin}book/{book['id']}",
                info=f"Author: {book.get('authorPseudonym')} | Chapters: {book.get('lastUpdateChapterOrder')}",
            )

    def read_novel(self, novel: Novel) -> None:
        match = re.search(r"/book/(\d+)", novel.url)
        if not match:
            raise LNException(f"Invalid novel URL: {novel.url}")
        book_id = match.group(1)

        book = self._api(f"books/{book_id}")
        novel.title = book["title"]
        novel.cover_url = book.get("coverImgUrl") or ""
        novel.author = book.get("authorPseudonym") or ""
        novel.synopsis = book.get("synopsis") or ""
        novel.tags = [t for t in (book.get("tag") or "").split(",") if t]

        items: list = []
        page, total_pages = 1, 1
        while page <= total_pages:
            data = self._api(
                "chapters/page",
                sortDirection="ASC",
                bookId=book_id,
                pageNumber=page,
                pageSize=100,
            )
            items += data["list"]
            total_pages = data["totalPages"]
            page += 1

        novel.volumes = []
        novel.chapters = []
        for item in items:
            if not self._is_readable(item):
                continue
            novel.add_chapter(
                title=item["title"],
                url=f"{self.scraper.origin}chapter/{item['id']}",
            )

    def download_chapter(self, chapter: Chapter) -> None:
        chapter_id = re.search(r"/chapter/(\d+)", chapter.url)
        if not chapter_id:
            raise LNException(f"Invalid chapter URL: {chapter.url}")
        data = self._api(f"chapters/{chapter_id.group(1)}")
        soup = self.scraper.make_soup(data["content"])
        chapter.body = self.cleaner.extract_contents(soup.select_one("body"))

    @staticmethod
    def _is_readable(item: Dict[str, Any]) -> bool:
        # Coin-paywalled and VIP early-access (tier > 0) chapters are locked for non-buyers.
        if item.get("status") != "published" or item.get("paywallStatus") != "free":
            return False
        return not item.get("tier") or bool(item.get("paid"))
