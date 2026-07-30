# -*- coding: utf-8 -*-
"""NovelDex (https://noveldex.io) source crawler.

Chapter HTML is delivered inside Next.js RSC flight data under `xorEncryption`
(base64 + FNV-1a keystream). Series TOC is embedded in the same flight payload
and paginated with `?page=N` (100 chapters per page).
"""

from __future__ import annotations

import base64
import json
import logging
import math
import re
from typing import Any, Dict, List, Optional
from urllib.parse import quote, urlparse

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)

_ORIGIN = "https://noveldex.io"
_CHAPTERS_PER_PAGE = 100
_ZW_RE = re.compile(r"[\u200B\u200C\u200D\u2060\uFEFF\u00AD\U000E0000-\U000E007F]+")
_HOMOGLYPHS = str.maketrans(
    {
        "\u0430": "a",
        "\u0441": "c",
        "\u0435": "e",
        "\u043e": "o",
        "\u0440": "p",
        "\u0445": "x",
        "\u0443": "y",
        "\u0410": "A",
        "\u0412": "B",
        "\u0421": "C",
        "\u0415": "E",
        "\u041d": "H",
        "\u041a": "K",
        "\u041c": "M",
        "\u041e": "O",
        "\u0420": "P",
        "\u0422": "T",
        "\u0425": "X",
    }
)
_SERIES_PATH_RE = re.compile(
    r"/series/(?P<kind>novel|comic)/(?P<slug>[^/]+)(?:/chapter/(?P<num>\d+))?",
    re.I,
)


def _fnv_key(partial_key_hint: str, timestamp: str, client_nonce: str) -> bytes:
    seed = f"{partial_key_hint}|{timestamp}|{client_nonce}"
    s = 0x811C9DC5
    for ch in seed:
        s ^= ord(ch)
        s = (s * 0x01000193) & 0xFFFFFFFF
    key = bytearray(32)
    for i in range(32):
        s ^= (i * 0x9E3779B9) & 0xFFFFFFFF
        s = (s * 0x01000193) & 0xFFFFFFFF
        key[i] = s & 0xFF
    return bytes(key)


def _xor_decrypt(encrypted_b64: str, key: bytes) -> str:
    pad = (-len(encrypted_b64)) % 4
    if pad:
        encrypted_b64 += "=" * pad
    data = base64.b64decode(encrypted_b64)
    out = bytes(b ^ key[i % len(key)] for i, b in enumerate(data))
    return out.decode("utf-8")


def _extract_flight(html: str) -> str:
    """Decode Next.js flight pushes into one text blob.

    Each push is a JS string; ``json.loads`` unescapes it without mangling UTF-8.
    """
    pushes = re.findall(r'self\.__next_f\.push\(\[1,"((?:\\.|[^"\\])*)"\]\)', html)
    if not pushes:
        return ""
    parts: List[str] = []
    for chunk in pushes:
        try:
            parts.append(json.loads(f'"{chunk}"'))
        except json.JSONDecodeError:
            parts.append(chunk)
    return "".join(parts)


def _resolve_rsc_ref(flight: str, ref: str) -> str:
    if not ref.startswith("$"):
        return ref
    num = ref[1:]
    m = re.search(rf"(?:^|\n){re.escape(num)}:T([0-9a-fA-F]+),", flight)
    if not m:
        m2 = re.search(rf'(?:^|\n){re.escape(num)}:"((?:\\.|[^"\\])*)"', flight)
        if not m2:
            raise ValueError(f"Cannot resolve RSC ref {ref}")
        try:
            return json.loads(f'"{m2.group(1)}"')
        except json.JSONDecodeError:
            return m2.group(1)
    length = int(m.group(1), 16)
    start = m.end()
    return flight[start : start + length]


def _json_balance(text: str, start: int, open_ch: str, close_ch: str) -> Optional[str]:
    depth = 0
    in_str = False
    esc = False
    for j, ch in enumerate(text[start:], start):
        if in_str:
            if esc:
                esc = False
            elif ch == "\\":
                esc = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start : j + 1]
    return None


def _extract_json_array(flight: str, key: str = '"chapters":') -> List[Dict[str, Any]]:
    i = flight.find(key)
    if i < 0:
        return []
    start = flight.find("[", i)
    if start < 0:
        return []
    raw = _json_balance(flight, start, "[", "]")
    if not raw:
        return []
    raw = raw.replace('"$undefined"', "null")
    try:
        data = json.loads(raw)
        return data if isinstance(data, list) else []
    except json.JSONDecodeError:
        return []


def _extract_object_with_slug(flight: str, slug: str) -> Optional[Dict[str, Any]]:
    marker = f'"slug":"{slug}"'
    idx = 0
    while True:
        i = flight.find(marker, idx)
        if i < 0:
            return None
        start = None
        depth = 0
        for k in range(i, max(0, i - 8000), -1):
            ch = flight[k]
            if ch == "}":
                depth += 1
            elif ch == "{":
                if depth == 0:
                    start = k
                    break
                depth -= 1
        if start is None:
            idx = i + 1
            continue
        raw = _json_balance(flight, start, "{", "}")
        if raw:
            raw = raw.replace('"$undefined"', "null")
            try:
                obj = json.loads(raw)
            except json.JSONDecodeError:
                obj = None
            if isinstance(obj, dict) and obj.get("slug") == slug:
                if any(k in obj for k in ("chapterCount", "description", "team", "coverImage")):
                    return obj
        idx = i + 1

def _series_kind(type_name: Optional[str]) -> str:
    t = (type_name or "").upper()
    if t in {"COMIC", "MANHWA", "MANHUA", "MANGA"}:
        return "comic"
    return "novel"


def _clean_content(html: str) -> str:
    html = _ZW_RE.sub("", html)
    html = html.translate(_HOMOGLYPHS)
    return html


class NovelDexCrawler(LegacyCrawler):
    base_url = [
        "https://noveldex.io/",
        "https://www.noveldex.io/",
    ]
    has_manga = False
    has_mtl = False
    can_search = True
    request_rate_limit = 1.5

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            {
                "script",
                "style",
                "noscript",
                "[data-xor-content] + *",
            }
        )

    def search_novel(self, query: str):
        data = self.get_json(f"{_ORIGIN}/api/search?q={quote(query)}")
        results = []
        for item in data.get("series") or []:
            slug = item.get("urlSlug") or item.get("slug")
            if not slug:
                continue
            kind = _series_kind(item.get("type"))
            title = item.get("title") or slug
            info_bits = []
            if item.get("type"):
                info_bits.append(str(item["type"]))
            if item.get("status"):
                info_bits.append(str(item["status"]))
            if item.get("chapterCount") is not None:
                info_bits.append(f"{item['chapterCount']} chapters")
            results.append(
                {
                    "title": title,
                    "url": f"{_ORIGIN}/series/{kind}/{slug}",
                    "info": " | ".join(info_bits),
                }
            )
        return results

    def read_novel_info(self) -> None:
        kind, slug = self._parse_series_url(self.novel_url)
        self.novel_url = f"{_ORIGIN}/series/{kind}/{slug}"
        self._series_kind = kind
        self._series_slug = slug

        page1 = self._fetch_series_page(1)
        series = page1["series"]
        chapters = list(page1["chapters"])

        self.novel_title = series.get("title") or slug
        team = series.get("team") or {}
        self.novel_author = team.get("name") or ""
        self.novel_synopsis = (series.get("description") or "").replace("\r\n", "\n")
        cover = series.get("coverImage") or ""
        if cover:
            self.novel_cover = self.absolute_url(cover, page_url=self.novel_url)

        genres = [g.get("name") for g in (series.get("genres") or []) if g.get("name")]
        tags = [t.get("name") for t in (series.get("tags") or []) if t.get("name")]
        self.novel_tags = [*(genres or []), *(tags or [])]

        chapter_count = int(series.get("chapterCount") or len(chapters) or 0)
        total_pages = max(1, math.ceil(chapter_count / _CHAPTERS_PER_PAGE))
        seen = {c.get("id") for c in chapters if c.get("id")}

        for page in range(2, total_pages + 1):
            more = self._fetch_series_page(page)["chapters"]
            for ch in more:
                cid = ch.get("id")
                if cid and cid in seen:
                    continue
                if cid:
                    seen.add(cid)
                chapters.append(ch)

        chapters.sort(key=lambda c: (c.get("number") is None, c.get("number") or 0))

        free_nums: list[int] = []
        locked_nums: list[int] = []
        next_free: Optional[Dict[str, Any]] = None
        for ch in chapters:
            number = ch.get("number")
            if number is None:
                continue
            locked = bool(ch.get("isLocked") and not ch.get("hasAccess"))
            if locked:
                locked_nums.append(int(number))
                if next_free is None and ch.get("becomesFreeAt"):
                    next_free = {
                        "number": int(number),
                        "title": ch.get("title") or f"Chapter {number}",
                        "becomesFreeAt": ch.get("becomesFreeAt"),
                        "coinPrice": ch.get("coinPrice"),
                    }
            else:
                free_nums.append(int(number))

        logger.info(
            "NovelDex TOC: reported=%s free=%s locked=%s free_range=%s..%s",
            chapter_count,
            len(free_nums),
            len(locked_nums),
            free_nums[0] if free_nums else None,
            free_nums[-1] if free_nums else None,
        )
        if next_free:
            logger.info(
                "NovelDex next free unlock: ch %s (%s) at %s (coins=%s)",
                next_free["number"],
                next_free["title"],
                next_free["becomesFreeAt"],
                next_free.get("coinPrice"),
            )
        # Exposed for tools/watchers via novel extras after read_novel.
        self.noveldex_free_count = len(free_nums)
        self.noveldex_locked_count = len(locked_nums)
        self.noveldex_next_free = next_free

        for ch in chapters:
            # Locked / unpaid chapters have no readable body until unlocked free.
            if ch.get("isLocked") and not ch.get("hasAccess"):
                continue
            number = ch.get("number")
            if number is None:
                continue
            title = ch.get("title") or f"Chapter {number}"
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append(Volume(id=vol_id))
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    title=title,
                    url=f"{_ORIGIN}/series/{kind}/{slug}/chapter/{number}",
                )
            )

        if not self.chapters:
            raise Exception("No accessible chapters found on NovelDex")

    def download_chapter_body(self, chapter: Chapter) -> str:
        html = self.get_response(chapter.url).text
        flight = _extract_flight(html)
        if not flight:
            raise Exception(f"No RSC flight data for {chapter.url}")

        xor = self._parse_xor(flight)
        if not xor:
            # Free preview HTML is sometimes present when encryption is off.
            m = re.search(
                r'"chapter"\s*:\s*\{[^{}]*?"content"\s*:\s*"(?P<body>(?:\\.|[^"\\])*)"',
                flight,
            )
            if m and m.group("body"):
                try:
                    body = json.loads(f'"{m.group("body")}"')
                except json.JSONDecodeError:
                    body = m.group("body")
                return self._to_clean_body(body)
            raise Exception(
                f"Chapter content unavailable (locked or missing encryption): {chapter.url}"
            )

        raw = _xor_decrypt(xor["encryptedBase64"], xor["key"])
        return self._to_clean_body(raw)

    def _to_clean_body(self, html: str) -> str:
        html = _clean_content(html)
        soup = self.make_soup(html)
        # PageSoup stringification re-wraps nodes in <html><body>; pass the
        # underlying bs4 body tag so the cleaner emits clean <p> paragraphs.
        root = soup.body
        if hasattr(root, "tag"):
            root = root.tag
        return self.cleaner.extract_contents(root)

    def _parse_series_url(self, url: str) -> tuple[str, str]:
        path = urlparse(url).path
        m = _SERIES_PATH_RE.search(path)
        if not m:
            raise Exception(f"Unrecognized NovelDex URL: {url}")
        return m.group("kind").lower(), m.group("slug")

    def _fetch_series_page(self, page: int) -> Dict[str, Any]:
        url = self.novel_url if page <= 1 else f"{self.novel_url}?page={page}"
        html = self.get_response(url).text
        flight = _extract_flight(html)
        if not flight:
            raise Exception(f"No RSC flight data for {url}")

        slug = getattr(self, "_series_slug", "")
        series = _extract_object_with_slug(flight, slug) if slug else None
        chapters = _extract_json_array(flight, '"chapters":')
        if page == 1 and not series:
            raise Exception(f"Could not parse series metadata from {url}")
        return {"series": series or {}, "chapters": chapters}

    def _parse_xor(self, flight: str) -> Optional[Dict[str, Any]]:
        m = re.search(
            r'"xorEncryption"\s*:\s*\{\s*'
            r'"encryptedBase64"\s*:\s*"(?P<b64>[^"]+)"\s*,\s*'
            r'"partialKeyHint"\s*:\s*"(?P<hint>[^"]+)"\s*,\s*'
            r'"timestamp"\s*:\s*(?P<ts>\d+)\s*,\s*'
            r'"clientNonce"\s*:\s*"(?P<nonce>[^"]+)"',
            flight,
        )
        if not m:
            return None
        b64 = _resolve_rsc_ref(flight, m.group("b64"))
        key = _fnv_key(m.group("hint"), m.group("ts"), m.group("nonce"))
        return {"encryptedBase64": b64, "key": key}
