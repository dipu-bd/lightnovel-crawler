# -*- coding: utf-8 -*-
import logging
from typing import Any, Dict, Optional

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)

# The site is a single-page app whose HTML carries no content. It reads this backend
# through a proxy worker of its own, which the app authenticates with a key it ships;
# the backend answers the same requests directly, so the key and the extra hop are
# both avoidable.
API_URL = "https://webapi.novelfulll.com/api"

# The largest page the chapter listing accepts. A novel here runs to a few thousand
# chapters, so the listing has to be walked to the end — stopping at the first page is
# how a source silently reports fifty chapters of a thousand.
PAGE_SIZE = 50


class WebnovelOnlineDotComCrawler(LegacyCrawler):
    base_url = "https://webnovelonline.com/"
    version = 1

    def _detail(self, book_id: str, page: int) -> Dict[str, Any]:
        data = self.get_json(
            f"{API_URL}/book/detail?bookId={book_id}"
            f"&page_num={page}&page_size={PAGE_SIZE}&language=en"
        )
        assert isinstance(data, dict) and data.get("code") == 0, "The API refused the request"
        return data["data"]

    def read_novel_info(self) -> None:
        book_id = self.novel_url.split("?")[0].strip("/").split("/")[-1]
        first = self._detail(book_id, 1)

        info = first["book_info"]
        self.novel_title = info["name"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = info.get("cover") or None
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = info.get("author") or ""
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = info.get("description") or ""
        self.novel_tags = [tag for tag in str(info.get("tag") or "").split(",") if tag]

        pages = [first]
        for page in range(2, int(first.get("total_page") or 1) + 1):
            pages.append(self._detail(book_id, page))

        for page_data in pages:
            for item in page_data.get("chapter_list") or []:
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=1 + len(self.chapters) // 100,
                        title=item.get("title") or f"Chapter {chap_id}",
                        url=f"{API_URL}/chapter/content?bookId={book_id}&chapterId={item['id']}",
                    )
                )

        expected = int(first.get("total_size") or 0)
        if expected and len(self.chapters) != expected:
            logger.warning(
                "Listed %d chapters but the API reports %d", len(self.chapters), expected
            )

    def download_chapter_body(self, chapter: Chapter) -> Optional[str]:
        data = self.get_json(chapter.url)
        if not isinstance(data, dict) or data.get("code") != 0:
            return None
        return ((data.get("data") or {}).get("book_content") or {}).get("content")
