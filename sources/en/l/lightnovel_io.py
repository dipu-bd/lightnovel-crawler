# -*- coding: utf-8 -*-

"""Crawler for lightnovel.to."""

import json
import re
from typing import Any, Iterable, Optional
from urllib.parse import urlparse

from lncrawl.core import Chapter, Novel, PageSoup, Volume
from lncrawl.templates.novelfull import NovelFullTemplate


class LightNovelIoCrawler(NovelFullTemplate):
    base_url = ["https://lightnovel.to/"]
    request_rate_limit = 1.0
    chapter_list_on_novel_page = True
    chapter_body_selector = "div.ln-prose"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "script",
                "style",
                "nav",
                "button",
                "iframe",
                "form",
            ]
        )

        self.cleaner.bad_css.update(
            [
                "header",
                "footer",
                "[class*='ad-']",
                "[class*='ads']",
                "[id*='ad-']",
                "[id*='ads']",
                "[class*='comment']",
                "[class*='navigation']",
            ]
        )

    def _json_ld(self, soup: PageSoup) -> dict[str, Any]:
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.get_text())
            except (TypeError, ValueError):
                continue

            items = data if isinstance(data, list) else data.get("@graph", [data])

            for item in items:
                if isinstance(item, dict) and item.get("@type") == "Book":
                    return item

        return {}

    def _get_slug(self, url: str) -> str:
        parts = [part for part in urlparse(url).path.split("/") if part]

        if "novel" not in parts:
            raise ValueError("LightNovel novel slug is missing")

        return parts[parts.index("novel") + 1]

    def _chapter_number(self, href: str) -> Optional[int]:
        match = re.search(r"/chapter-(\d+)", href or "")
        return int(match.group(1)) if match else None

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        title = soup.select_one("h1.ln-dtitle") or soup.select_one("h1")

        if title:
            novel.title = title.get_text(" ", strip=True)

        if not novel.title:
            novel.title = self._json_ld(soup).get("name", "")

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        author = self._json_ld(soup).get("author", [])

        if isinstance(author, dict):
            author = [author]

        novel.author = ", ".join(
            item.get("name", "").strip()
            for item in author
            if isinstance(item, dict) and item.get("name")
        )

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        novel.cover_url = self._json_ld(soup).get("image", "")

        if not novel.cover_url:
            image = soup.select_one("img[alt]")

            if image:
                novel.cover_url = image.get("src", "")

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        description = self._json_ld(soup).get("description", "")

        if description:
            novel.synopsis = f"<p>{description}</p>"

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        genre = self._json_ld(soup).get("genre", [])

        if isinstance(genre, str):
            novel.tags = [genre]
        else:
            novel.tags = list(genre or [])

    def _visible_chapter_links(
        self,
        soup: PageSoup,
    ) -> dict[int, tuple[str, str]]:
        chapters: dict[int, tuple[str, str]] = {}

        for anchor in soup.select(
            '.ln-crow a[href*="/novel/"][href*="/chapter-"]'
        ):
            href = anchor.get("href", "")
            number = self._chapter_number(href)

            if number is None:
                continue

            text = anchor.get_text(" ", strip=True)

            match = re.search(
                r"Chapter\s+\d+\s*(?:-\s*\d+)?\s*:\s*(.*)$",
                text,
                re.IGNORECASE,
            )

            if match:
                title = f"Chapter {number}: {match.group(1).strip()}"
            else:
                title = f"Chapter {number}"

            chapters[number] = (
                title,
                self.absolute_url(href),
            )

        return chapters

    def _total_chapters(self, soup: PageSoup) -> int:
        text = soup.get_text(" ", strip=True)

        matches = re.findall(
            r"with\s+([\d,]+)\s+chapters?",
            text,
            re.IGNORECASE,
        )

        if matches:
            return int(matches[0].replace(",", ""))

        return 0

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        return tag.select(
            '.ln-crow a[href*="/novel/"][href*="/chapter-"]'
        )

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        slug = self._get_slug(novel.url)
        visible = self._visible_chapter_links(soup)
        total = self._total_chapters(soup)

        if not total:
            total = max(visible.keys(), default=0)

        novel.volumes = [Volume(id=1)]
        novel.chapters = []

        for number in range(1, total + 1):
            title, url = visible.get(
                number,
                (
                    f"Chapter {number}",
                    f"https://lightnovel.to/novel/{slug}/chapter-{number}",
                ),
            )

            novel.chapters.append(
                Chapter(
                    id=number,
                    volume=1,
                    title=title,
                    url=url,
                )
            )

    def parse_chapter_item(
        self,
        soup: PageSoup,
        chapter_id: int,
    ) -> Chapter:
        href = soup.get("href", "")
        number = self._chapter_number(href) or chapter_id
        text = soup.get_text(" ", strip=True)

        match = re.search(
            r"Chapter\s+\d+\s*(?:-\s*\d+)?\s*:\s*(.*)$",
            text,
            re.IGNORECASE,
        )

        title = (
            f"Chapter {number}: {match.group(1).strip()}"
            if match
            else f"Chapter {number}"
        )

        return Chapter(
            id=chapter_id,
            title=title,
            url=self.absolute_url(href),
        )

    def parse_chapter_body(
        self,
        soup: PageSoup,
        chapter: Chapter,
    ) -> None:
        if soup is None:
            chapter.body = ""
            return

        # `soup` is already the selected `.ln-prose` element.
        chapter.body = self.cleaner.extract_contents(soup)