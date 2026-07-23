# -*- coding: utf-8 -*-
import json
import logging
import time
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import quote, urlparse

from lncrawl.core import Chapter, Novel, PageSoup, Volume
from lncrawl.exceptions import LNException
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelArrowCrawler(NovelFullTemplate):
    base_url = ["https://novelarrow.com/"]

    _api_headers = {
        "accept": "application/json",
        "x-client-platform": "web-desktop",
        "x-device-type": "desktop",
        "x-site-host": "novelarrow.com",
        "x-version-app": "web-desktop",
    }
    request_rate_limit = 4

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["script", "style", "nav", "button", "iframe"])
        self.cleaner.bad_css.update(
            [
                "aside",
                "header",
                "footer",
                "[class*='ads']",
                "[id*='ads']",
                "[class*='comment']",
                "[class*='navigation']",
            ]
        )

    def _get_slug(self, url: str) -> str:
        parts = [part for part in urlparse(url).path.split("/") if part]
        if "novel" in parts:
            return parts[parts.index("novel") + 1]
        if "chapter" in parts:
            return parts[parts.index("chapter") + 1]
        raise LNException("NovelArrow novel slug is missing")

    def _get_chapter_id(self, url: str) -> str:
        parts = [part for part in urlparse(url).path.split("/") if part]
        if "chapter" in parts:
            return parts[parts.index("chapter") + 2]
        return parts[-1]

    def _api_url(self, path: str) -> str:
        return f"{self.scraper.origin.rstrip('/')}/api-web/{path.lstrip('/')}"

    def _get_json(self, path: str) -> Any:
        url = self._api_url(path)
        error: Optional[Exception] = None
        for attempt in range(1, 6):
            try:
                response = self.scraper.get(url, headers=self._api_headers, timeout=30)
                if response.ok and response.text.strip():
                    return response.json()
                raise LNException(f"Empty response ({response.status_code}) from {url}")
            except Exception as e:
                error = e
                logger.debug(
                    "NovelArrow API request failed (%s/5): %s",
                    attempt,
                    url,
                    exc_info=True,
                )
                time.sleep(0.75 * attempt)
        raise LNException(f"NovelArrow API request failed: {url}") from error

    def _extract_payload(self, soup: PageSoup) -> Dict[str, Any]:
        for script in soup.select("script"):
            text = script.get_text()
            if "initialChapterList" not in text:
                continue

            try:
                encoded = text.split("self.__next_f.push([1,", 1)[1].rsplit("])", 1)[0]
                decoded = json.loads(encoded)
            except Exception:
                logger.debug("Failed to decode NovelArrow Next.js payload", exc_info=True)
                continue

            marker = decoded.find('"initialChapterList"')
            for start in range(marker, -1, -1):
                if decoded[start] != "{":
                    continue
                try:
                    payload, _ = json.JSONDecoder().raw_decode(decoded[start:])
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict) and "initialChapterList" in payload:
                    return payload

        return {}

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        payload = self._extract_payload(soup)
        novel.title = payload.get("title") or self._meta_content(soup, "og:novel:novel_name")
        if not novel.title:
            super().parse_title(soup, novel)

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        payload = self._extract_payload(soup)
        novel.cover_url = payload.get("coverImage") or self._meta_content(soup, "og:image")
        if not novel.cover_url:
            super().parse_cover(soup, novel)

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        payload = self._extract_payload(soup)
        novel.author = payload.get("author") or self._meta_content(soup, "og:novel:author")
        if not novel.author:
            super().parse_authors(soup, novel)

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        payload = self._extract_payload(soup)
        novel.tags = [
            genre.get("label", "").strip()
            for genre in payload.get("genres", [])
            if genre.get("label", "").strip()
        ]
        if not novel.tags:
            content = self._meta_content(soup, "og:novel:genre")
            novel.tags = [tag.strip() for tag in content.split(",") if tag.strip()]

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        payload = self._extract_payload(soup)
        paragraphs = payload.get("synopsisParagraphs") or []
        if paragraphs:
            novel.synopsis = "".join(
                f"<p>{paragraph.strip()}</p>" for paragraph in paragraphs if paragraph.strip()
            )
            return
        super().parse_summary(soup, novel)

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[Dict[str, Any]]:
        slug = self._get_slug(novel.url)
        self._novel_slug = slug
        logger.info("Fetching NovelArrow chapter list: %s", slug)
        data = self._get_json(f"novels/{quote(slug)}/chapters?sort=asc")
        chapters: List[Dict[str, Any]] = data if isinstance(data, list) else data.get("items", [])
        logger.info("NovelArrow chapters found: %s", len(chapters))
        return chapters

    def parse_chapter_item(self, soup: Dict[str, Any], chapter_id: int) -> Chapter:
        novel_slug = getattr(self, "_novel_slug", "")
        chapter_slug = soup.get("chapter_id", "").strip()
        return Chapter(
            id=chapter_id,
            title=soup.get("chapter_name", "").strip(),
            url=f"{self.scraper.origin}chapter/{quote(novel_slug)}/{quote(chapter_slug)}",
        )

    def download_chapter(self, chapter: Chapter) -> None:
        novel_slug = self._get_slug(chapter.url)
        chapter_slug = self._get_chapter_id(chapter.url)
        data = self._get_json(f"novels/{quote(novel_slug)}/chapters/{quote(chapter_slug)}")
        item = data.get("item", data)
        info = item.get("chapterInfo", item)
        if info.get("chapter_name"):
            chapter.title = info["chapter_name"]
        html = info.get("chapter_content", "")
        if not html:
            raise LNException("NovelArrow chapter content is missing")

        soup = PageSoup.create(html)
        self.cleaner.clean_contents(soup)
        body = soup.select_one("body") or soup
        chapter.body = body.inner_html

    def _meta_content(self, soup: PageSoup, name: str) -> str:
        tag = soup.select_one(f'meta[name="{name}"], meta[property="{name}"]')
        return tag.get("content", "").strip() if tag else ""
