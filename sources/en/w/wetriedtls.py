# -*- coding: utf-8 -*-
import base64
import json
import re
from typing import List
from urllib.parse import urlparse

from lncrawl.core import Chapter, Novel, SoupTemplate
from lncrawl.exceptions import LNException

series_url = "https://api.wetriedtls.com/series/{}"
chapters_url = "https://api.wetriedtls.com/chapters/{}?page={}&perPage=100&order=asc"

# The site is a Next.js app; a chapter's HTML body arrives base64-encoded inside a
# React Server Component flight payload rather than in the page's static markup.
FLIGHT_LINE_PATTERN = re.compile(r"self\.__next_f\.push\((\[.+)\)$")
TEXT_CHUNK_PATTERN = re.compile(r"^[0-9a-fA-F]+:T[0-9a-fA-F]*,(.*)", re.DOTALL)
CHUNK_SPLIT_PATTERN = re.compile(r"\n(?=[0-9a-fA-F]+:)")


class WeTriedTlsCrawler(SoupTemplate):
    base_url = "https://wetriedtls.com/"
    language = "en"

    def initialize(self) -> None:
        self.cleaner.bad_tag_text_pairs["p"] = re.compile(
            r"we\s*tried\s*translations"
            r"|translator\s*[:/]"
            r"|editor\s*:"
            r"|discord\.(com|gg)"
            r"|dsc\.gg"
            r"|join our discord",
            re.I,
        )

    def read_novel(self, novel: Novel) -> None:
        slug = urlparse(novel.url).path.strip("/").split("/")[-1]
        data = self.scraper.get_json(series_url.format(slug))

        novel.title = data["title"]
        novel.cover_url = data["thumbnail"]
        novel.author = data.get("author") or ""
        novel.synopsis = data.get("description") or ""
        novel.tags = [tag["name"] for tag in data.get("tags") or [] if tag.get("name")]

        series_id = data["id"]
        page_1 = self.scraper.get_json(chapters_url.format(series_id, 1))
        items = list(page_1["data"])

        last_page = page_1["meta"]["last_page"]
        futures = [
            self.taskman.submit_task(self.scraper.get_json, chapters_url.format(series_id, page))
            for page in range(2, last_page + 1)
        ]
        for page_data in self.taskman.resolve(futures, desc="Chapters", unit="page"):
            if page_data:
                items += page_data["data"]

        items.sort(key=lambda item: float(item["index"]))
        for item in items:
            novel.add_chapter(
                url=f"{novel.url}/{item['chapter_slug']}",
                title=item.get("chapter_name") or item["chapter_title"],
            )

    def download_chapter(self, chapter: Chapter) -> None:
        html = self.scraper.get(chapter.url).text
        content = self._extract_chapter_html(html)
        soup = self.scraper.make_soup(content)
        chapter.body = self.cleaner.extract_contents(soup.select_one("body"))

    def _extract_chapter_html(self, html: str) -> str:
        """Pull the chapter body out of the page's Next.js flight payload.

        The payload is a sequence of `id:Tlen,<text-or-base64>` chunks; the chapter
        body is whichever decoded chunk is itself an HTML fragment (others are script
        metadata, icon SVG paths, etc.), so pick the first one that looks like markup
        rather than trusting a fixed chunk index.
        """
        decoded: List[str] = []
        for script in re.findall(r"<script[^>]*>(.*?)</script>", html, re.DOTALL):
            for line in script.splitlines():
                match = FLIGHT_LINE_PATTERN.search(line)
                if not match:
                    continue
                try:
                    chunk = json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue
                if not isinstance(chunk, list) or len(chunk) < 2:
                    continue
                kind, value = chunk[0], chunk[1]
                if not isinstance(value, str):
                    continue
                if kind == 1:
                    decoded.append(value)
                elif kind == 3:
                    try:
                        decoded.append(base64.b64decode(value).decode("utf-8", "replace"))
                    except (ValueError, UnicodeDecodeError):
                        continue

        for chunk_text in decoded:
            for piece in CHUNK_SPLIT_PATTERN.split(chunk_text):
                text_match = TEXT_CHUNK_PATTERN.match(piece)
                body = text_match.group(1) if text_match else piece
                body = body.strip()
                if body.startswith("<p"):
                    return body

        raise LNException("Could not locate chapter content")
