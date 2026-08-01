# -*- coding: utf-8 -*-
import logging
import re
from typing import Any, Dict, Iterable, List
import unicodedata
from urllib.parse import urlparse

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)

API_URL = "https://api.skynovels.net/api"
IMAGE_URL = "https://api.skynovels.net/api/get-image"
NOVEL_ID = re.compile(r"/(\d+)(?:/|$)")
CATALOGUE_SIZE = 500


def fold(text: str) -> str:
    """Lowercase and strip accents, so `evolucion` finds `Evolución`."""
    stripped = unicodedata.normalize("NFD", text or "")
    return "".join(c for c in stripped if not unicodedata.combining(c)).lower()


class SkyNovelsCrawler(SoupTemplate):
    base_url = ["https://www.skynovels.net/"]

    can_search = True

    def initialize(self) -> None:
        self.catalogue: List[Dict[str, Any]] = []

    def read_catalogue(self) -> List[Dict[str, Any]]:
        # The whole library is a few hundred entries and there is no per-novel detail
        # route, so one listing request answers both search and the synopsis lookup.
        if not self.catalogue:
            data = self.scraper.get_json(f"{API_URL}/novels?limit={CATALOGUE_SIZE}")
            self.catalogue = data.get("novels") or []
        return self.catalogue

    def search(self, query: str) -> Iterable[SearchResult]:
        needle = fold(query.strip())
        for item in self.read_catalogue():
            title = item.get("nvl_title") or ""
            if needle in fold(title):
                yield SearchResult(
                    title=title,
                    url=f"https://www.skynovels.net/novelas/{item['id']}/{item['nvl_name']}",
                    info=item.get("nvl_writer") or "",
                )

    def read_novel(self, novel: Novel) -> None:
        # Every path on this Angular app answers 200, so the route says nothing about
        # whether a novel exists — the numeric id in the URL is the only real key.
        match = NOVEL_ID.search(urlparse(self.absolute_url(novel.url)).path)
        if not match:
            raise ValueError("no novel id in the url; expected /novelas/<id>/<slug>")
        novel_id = match.group(1)

        payload = self.scraper.get_json(f"{API_URL}/novel-chapters/{novel_id}")["novel"][0]

        novel.title = payload.get("nvl_title") or ""
        novel.author = payload.get("nvl_writer") or payload.get("nvl_translator") or ""
        novel.language = novel.language or self.language

        # The chapter route omits the synopsis; only the listing carries it.
        entry = next((n for n in self.read_catalogue() if str(n.get("id")) == novel_id), {})
        if entry.get("nvl_content"):
            novel.synopsis = self.cleaner.extract_contents(PageSoup.create(entry["nvl_content"]))
        if payload.get("image"):
            novel.cover_url = f"{IMAGE_URL}/{payload['image']}/novels/false"

        # `chp_index_title` looks like a volume name but is neither reliable nor useful —
        # some novels repeat "Volumen 1" on every chapter, others just restate the number.
        # Grouping by it made one volume per chapter, and printing it gave "Capítulo 1 -
        # Capitulo 1". The API carries no real chapter title, so the number is the title.
        for item in sorted(payload.get("chapters") or [], key=lambda c: c.get("chp_number") or 0):
            if item.get("chp_status") != "Active":
                continue
            novel.add_chapter(
                title=f"Capítulo {item.get('chp_number')}",
                url=f"{API_URL}/chapters/{item['id']}",
            )

    def download_chapter(self, chapter: Chapter) -> None:
        payload = self.scraper.get_json(self.absolute_url(chapter.url))["chapter"]
        if isinstance(payload, list):
            payload = payload[0] if payload else {}
        chapter.body = self.cleaner.extract_contents(
            PageSoup.create(payload.get("chp_content") or "")
        )
