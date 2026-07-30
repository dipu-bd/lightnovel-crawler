# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, List, Optional

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)

# The site is a single-page app: the HTML is an empty shell and every field is fetched
# from this backend, which is the same one the app itself talks to.
API_URL = "https://debebcxopcfhukeqweco.supabase.co/rest/v1"

# Published only. The app also lists "scheduled" chapters, which carry a title and no
# body yet, and storing those is how a library fills up with empty chapters.
CHAPTER_FILTER = "status=eq.published"


class WordExcerptCrawler(LegacyCrawler):
    base_url = ["https://wordexcerpt.com/"]
    version = 1

    def initialize(self) -> None:
        self._api_key = ""

    @property
    def api_key(self) -> str:
        """The app's public API key, read from the script it ships.

        Hardcoding it would work until the key is rotated, and the failure then is a
        401 on every novel at once. The app has to hand the key to the browser, so
        taking it from where the browser gets it keeps the two in step.
        """
        if self._api_key:
            return self._api_key
        home = self.get_response(self.home_url).text or ""
        entry = re.search(r'src="(/assets/index-[^"]+\.js)"', home)
        assert entry, "Could not locate the site's script bundle"
        bundle = self.get_response(self.absolute_url(entry.group(1))).text or ""
        found = re.search(r"(eyJ[A-Za-z0-9_\-.]{60,})", bundle)
        assert found, "Could not locate the site's API key"
        self._api_key = found.group(1)
        return self._api_key

    def _query(self, path: str) -> List[Any]:
        key = self.api_key
        data = self.get_json(
            f"{API_URL}/{path}",
            headers={"apikey": key, "Authorization": f"Bearer {key}"},
        )
        return data if isinstance(data, list) else []

    def read_novel_info(self) -> None:
        slug = self.novel_url.split("?")[0].strip("/").split("/")[-1]
        rows = self._query(f"novels?slug=eq.{slug}&select=*&limit=1")
        assert rows, "No novel found"
        novel = rows[0]

        self.novel_title = novel["title"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = novel.get("cover_url") or None
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = novel.get("author_name") or ""
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = novel.get("synopsis") or ""
        self.novel_tags = list(novel.get("genres") or []) + list(novel.get("tags") or [])

        chapters = self._query(
            f"chapters?novel_id=eq.{novel['id']}&{CHAPTER_FILTER}"
            f"&select=id,number,title&order=number.asc"
        )
        for chapter in chapters:
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=1 + len(self.chapters) // 100,
                    title=chapter.get("title") or f"Chapter {chapter.get('number', chap_id)}",
                    url=f"{API_URL}/chapters?id=eq.{chapter['id']}&select=content",
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> Optional[str]:
        rows = self._query(chapter.url.replace(f"{API_URL}/", ""))
        return rows[0].get("content") if rows else None
