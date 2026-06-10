# -*- coding: utf-8 -*-

import html
import json
import logging
import random
import re
import threading
import time
from urllib.parse import parse_qs, urlencode, urlparse

import requests

from lncrawl.core import Chapter, LegacyCrawler, SearchResult, Volume

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------
# Regex helpers
# ----------------------------------------------------------------------

_RE_CHINESE_CHARS = re.compile(r"[\u4e00-\u9fff]")
_RE_HTML_TAG = re.compile(r"<[^>]+>")
_RE_WHITESPACE_COLLAPSE = re.compile(r"[ \t]{2,}")
_RE_BLANK_LINES = re.compile(r"\n{3,}")
_RE_TRAILING_WS = re.compile(r"[ \t]+\n")
_RE_LEADING_WS = re.compile(r"\n[ \t]+")
_RE_CR = re.compile(r"\r\n?")
_RE_PARAGRAPH_SPLIT = re.compile(r"\n{2,}")
_RE_PUNCT_BEFORE_UPPER = re.compile(r"([.!?])(?=[\"'\u201c\u201d\u2018\u2019]?[A-Z])")
_RE_PUNCT_BEFORE_LETTER = re.compile(r"([,;:])(?=[A-Za-z])")

_RE_DISCLAIMER_ZH = re.compile(r"温馨提示:.*?(敬请谅解!|$)", re.DOTALL)
_RE_DISCLAIMER_EN = re.compile(
    r"Friendly reminder:.*?(inconvenience caused!|$)",
    re.DOTALL | re.IGNORECASE,
)

_RE_SECURITY_CHECK = re.compile(
    r"("
    r"please complete the security check|"
    r"please complete the turnstile challenge|"
    r"complete the turnstile challenge|"
    r"turnstile challenge|"
    r"unusual reading activity|"
    r"complete the challenge below|"
    r"complete the challenge|"
    r"cf-turnstile|"
    r"cloudflare|"
    r"challenge-platform|"
    r"checking if the site connection is secure"
    r")",
    re.IGNORECASE,
)


class WtrLab(LegacyCrawler):
    """
    WTR-LAB crawler.

    Important:
    - This version does not bypass Cloudflare, Turnstile, or any security challenge.
    - If WTR-LAB asks for a security check, this crawler pauses and retries later.
    - If the challenge is still present after the configured pauses, it raises RuntimeError.
    - It does not return empty chapter bodies, to avoid saving bad .zst chapter files.
    - Final chapter output is plain text with paragraph breaks, not <p> HTML.
    """

    base_url = ["https://wtr-lab.com", "https://www.wtr-lab.com"]
    has_mtl = True

    # Keep this at 1. More workers can trigger Cloudflare/Turnstile quickly.
    workers = 1

    decrypt_proxy_url = "https://wtr-lab-proxy.fly.dev/chapter"

    translate_url = "https://translate-pa.googleapis.com/v1/translateHtml"
    translate_api_key = "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520"

    google_chunk_chars = 4500
    google_chunk_delay = 0.35

    # ------------------------------------------------------------------
    # Rate-limit controls
    # ------------------------------------------------------------------
    # Each WTR-LAB request waits approximately:
    # request_min_delay + random(0, request_jitter)
    #
    # Example:
    # 12 + random(0, 10) = 12 to 22 seconds.
    #
    # If you still get Turnstile, increase these.
    # If it is too slow and stable, test lower values gradually.
    request_min_delay = 4.0
    request_jitter = 8.0

    # Keep low. Aggressive retries make blocking worse.
    request_retries = 1

    throttled_statuses = {403, 408, 409, 425, 429, 500, 502, 503, 504}

    # Do NOT skip missing chapters.
    # Returning "" can make lncrawl save empty/bad .zst files.
    skip_missing_chapters = False

    # ------------------------------------------------------------------
    # Auto-pause controls for security-check / Turnstile detection
    # ------------------------------------------------------------------

    pause_on_security_check = True

    # 900 = 15 minutes, 1800 = 30 minutes.
    security_pause_seconds = 20

    # Number of pause+retry cycles before failing.
    security_pause_retries = 1

    # If True, waits for you to complete Turnstile manually and press Enter.
    # Useful when you are at the PC watching the terminal.
    security_pause_wait_for_enter = False

    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    )

    _body_paths = (
        ("data", "data", "body"),
        ("data", "data", "content"),
        ("data", "data", "text"),
        ("data", "data", "html"),
        ("data", "chapter", "body"),
        ("data", "chapter", "content"),
        ("data", "body"),
        ("data", "content"),
        ("data", "text"),
        ("chapter", "body"),
        ("chapter", "content"),
        ("chapter", "text"),
        ("body",),
        ("content",),
        ("text",),
        ("html",),
    )

    # ------------------------------------------------------------------
    # Init
    # ------------------------------------------------------------------

    def initialize(self) -> None:
        super().initialize()

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
                "User-Agent": self.user_agent,
            }
        )

        self._request_lock = threading.Lock()
        self._last_request_at = 0.0

        self.init_executor(workers=self.workers)

    # ------------------------------------------------------------------
    # Request / pause helpers
    # ------------------------------------------------------------------

    def _sleep_before_request(self) -> None:
        """
        Serialize WTR-LAB requests and add delay/jitter.

        This is not a Cloudflare/Turnstile bypass. It only avoids aggressive traffic.
        """
        with self._request_lock:
            delay = self.request_min_delay + random.uniform(0, self.request_jitter)
            elapsed = time.monotonic() - self._last_request_at
            wait = delay - elapsed

            if wait > 0:
                time.sleep(wait)

            self._last_request_at = time.monotonic()

    def _pause_for_security_check(self, reason: str) -> None:
        """
        Pause when WTR-LAB returns a security-check / Turnstile response.

        This does not bypass the challenge. It simply stops making requests for a while
        or waits for the user to manually complete the challenge in a browser.
        """
        if not self.pause_on_security_check:
            raise RuntimeError(reason)

        logger.warning("=" * 80)
        logger.warning("WTR-LAB security check detected.")
        logger.warning(reason)
        logger.warning(
            "The crawler is pausing to avoid saving bad .zst chapters. "
            "Complete the challenge manually in your browser if needed."
        )

        if self.security_pause_wait_for_enter:
            logger.warning("Complete the WTR-LAB Turnstile/security check, then press Enter.")
            input("Press Enter after completing the WTR-LAB security check...")
        else:
            logger.warning(
                "Pausing for %.0f seconds before retrying.",
                self.security_pause_seconds,
            )
            time.sleep(self.security_pause_seconds)

        logger.warning("Retrying after security-check pause.")
        logger.warning("=" * 80)

    def _headers(self, referer: str | None = None, content_type: str | None = None) -> dict:
        root = self._site_root() if getattr(self, "novel_url", None) else self.base_url[0]

        headers = {
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.9",
            "Origin": root,
            "Referer": referer or f"{root}/",
            "User-Agent": self.user_agent,
        }

        if content_type:
            headers["Content-Type"] = content_type

        return headers

    def _polite_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """
        Request with slow pacing, minimal retry, and Turnstile/security-check detection.

        If a security-check page is detected, pause and retry.
        If still challenged after security_pause_retries, raise RuntimeError.
        """
        last_error = None
        request_errors = 0
        security_pauses = 0
        throttle_retries = 0

        while True:
            self._sleep_before_request()

            try:
                resp = self.session.request(method, url, **kwargs)

                text_preview = resp.text[:5000] if resp.text else ""
                if _RE_SECURITY_CHECK.search(text_preview):
                    reason = (
                        "WTR-LAB is asking for a Turnstile/security check because it "
                        "detected unusual reading activity."
                    )

                    if security_pauses < self.security_pause_retries:
                        security_pauses += 1
                        self._pause_for_security_check(
                            reason
                            + f" Pause retry {security_pauses}/{self.security_pause_retries}."
                        )
                        continue

                    raise RuntimeError(
                        reason + " Security-check pause retries were exhausted. "
                        "Stopping to avoid saving bad chapter .zst files."
                    )

                if resp.status_code in self.throttled_statuses:
                    throttle_retries += 1

                    if throttle_retries > self.request_retries:
                        raise RuntimeError(
                            f"WTR-LAB returned status {resp.status_code} after "
                            f"{self.request_retries} retry attempt(s). Stopping."
                        )

                    retry_after = resp.headers.get("Retry-After")
                    if retry_after and retry_after.isdigit():
                        sleep_for = min(int(retry_after), 180)
                    else:
                        sleep_for = min(
                            30 * throttle_retries + random.uniform(10, 30),
                            180,
                        )

                    logger.warning(
                        "WTR-LAB throttled/challenged the request: "
                        "status=%s retry=%s/%s url=%s; sleeping %.1fs",
                        resp.status_code,
                        throttle_retries,
                        self.request_retries,
                        url,
                        sleep_for,
                    )
                    time.sleep(sleep_for)
                    continue

                resp.raise_for_status()
                return resp

            except RuntimeError:
                raise

            except requests.RequestException as exc:
                last_error = exc
                request_errors += 1

                if request_errors > self.request_retries:
                    raise RuntimeError(
                        f"Request failed after {self.request_retries} retry attempt(s): {url}"
                    ) from exc

                sleep_for = min(15 * request_errors + random.uniform(5, 15), 90)
                logger.warning(
                    "Request failed: retry=%s/%s url=%s error=%r; sleeping %.1fs",
                    request_errors,
                    self.request_retries,
                    url,
                    exc,
                    sleep_for,
                )
                time.sleep(sleep_for)

        if last_error:
            raise last_error

    def _polite_json_request(self, method: str, url: str, **kwargs):
        resp = self._polite_request(method, url, **kwargs)

        try:
            return resp.json()
        except ValueError as exc:
            preview = resp.text[:500] if resp.text else ""
            raise RuntimeError(
                f"Expected JSON but received non-JSON response: {preview!r}"
            ) from exc

    # ------------------------------------------------------------------
    # Search
    # ------------------------------------------------------------------

    def search_novel(self, query: str):
        data = self._polite_json_request(
            "POST",
            "https://www.wtr-lab.com/api/search",
            json={"text": query},
            headers=self._headers(
                referer="https://www.wtr-lab.com/",
                content_type="application/json",
            ),
            timeout=45,
        )

        results = []

        for novel in data.get("data", []):
            raw_id = novel.get("raw_id")
            slug = novel.get("slug")

            if not raw_id or not slug:
                continue

            novel_data = novel.get("data") or {}

            meta = {
                "Chapters": novel.get("chapter_count"),
                "Author": novel_data.get("author"),
                "Status": "Ongoing" if novel.get("status") else "Completed",
            }

            results.append(
                SearchResult(
                    url=f"https://www.wtr-lab.com/en/novel/{raw_id}/{slug}",
                    title=novel_data.get("title"),
                    info=" | ".join(f"{k}: {v}" for k, v in meta.items() if v),
                )
            )

        return results

    # ------------------------------------------------------------------
    # Novel metadata
    # ------------------------------------------------------------------

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        if _RE_SECURITY_CHECK.search(str(soup)[:5000]):
            raise RuntimeError(
                "WTR-LAB returned a Turnstile/security-check page while loading "
                "novel metadata. Complete the challenge manually in your browser "
                "and retry later."
            )

        script = soup.select_one("script#__NEXT_DATA__")
        if not script:
            raise RuntimeError("No __NEXT_DATA__ script found")

        page_props = json.loads(script.string)["props"]["pageProps"]
        series_data = page_props["serie"]["serie_data"]
        data = series_data.get("data") or {}

        self.novel_title = data.get("title")
        self.novel_cover = data.get("image")
        self.novel_synopsis = _strip_html(data.get("description") or "")
        self.novel_author = data.get("author")

        tags = page_props.get("tags") or []
        self.novel_tags = (
            [tag["title"] for tag in tags if tag.get("title")]
            if tags
            else [str(genre) for genre in series_data.get("genres", [])]
        )

        self.language = self._language_from_url(self.novel_url)

        self._build_chapter_list(
            raw_id=int(series_data["raw_id"]),
            chapter_count=int(series_data["chapter_count"]),
        )

    def _build_chapter_list(self, raw_id: int, chapter_count: int) -> None:
        root = self._site_root()
        language = self.language or "en"

        for chapter_no in range(1, chapter_count + 1):
            volume_id = (chapter_no - 1) // 100 + 1

            if chapter_no % 100 == 1:
                self.volumes.append(
                    Volume(
                        id=volume_id,
                        title=f"Volume {volume_id}",
                    )
                )

            qs = urlencode(
                {
                    "language": language,
                    "raw_id": raw_id,
                    "chapter_no": chapter_no,
                    "translate": "web",
                }
            )

            self.chapters.append(
                Chapter(
                    id=chapter_no,
                    url=f"{root}/api/reader/get?{qs}",
                    title=f"Chapter {chapter_no}",
                    volume=volume_id,
                    volume_title=f"Volume {volume_id}",
                    raw_id=raw_id,
                    language=language,
                    translate="web",
                )
            )

    # ------------------------------------------------------------------
    # Chapter download
    # ------------------------------------------------------------------

    def download_chapter_body(self, chapter):
        raw_id = self._attr_or_qs(chapter, "raw_id")
        if raw_id is None:
            raise RuntimeError(f"No raw_id in chapter URL: {chapter.url}")

        raw_id = int(raw_id)
        chapter_no = int(chapter.id)

        language = self._attr_or_qs(chapter, "language") or getattr(self, "language", None) or "en"

        reader = self._fetch_reader(
            raw_id=raw_id,
            chapter_no=chapter_no,
            language=language,
        )

        self._apply_title(chapter, reader)

        body = self._extract_body(reader)

        # Minimal fallback:
        # If English web translation has no body, try Chinese once.
        # Do not try many combinations because that can trigger security checks faster.
        if not body and language.lower() == "en":
            try:
                fallback_reader = self._fetch_reader(
                    raw_id=raw_id,
                    chapter_no=chapter_no,
                    language="zh-CN",
                )
                fallback_body = self._extract_body(fallback_reader)

                if fallback_body:
                    reader = fallback_reader
                    body = fallback_body

            except Exception as exc:
                logger.debug(
                    "Chinese fallback failed: raw_id=%s ch=%s error=%r",
                    raw_id,
                    chapter_no,
                    exc,
                )

        if not body:
            message = f"No body: raw_id={raw_id}, ch={chapter_no}"

            if self._looks_like_block_or_empty(reader):
                message += " — possible WTR-LAB block/security response"

            raise RuntimeError(message)

        if self._is_encrypted(body):
            body = self._decrypt(body)

        text = self._to_plain_text(body)

        # Important:
        # Never return a Turnstile/security-check page as chapter content.
        # That would be saved as a bad .zst chapter.
        if _RE_SECURITY_CHECK.search(text):
            text = self._retry_chapter_after_security_pause(
                raw_id=raw_id,
                chapter_no=chapter_no,
                language=language,
            )

        if not text:
            raise RuntimeError(f"Empty after body cleanup: raw_id={raw_id}, ch={chapter_no}")

        if language.lower() == "en" and self._looks_chinese(text):
            text = self._translate_zh_en(text)

            if self._looks_chinese(text):
                raise RuntimeError(f"Translation failed for chapter {chapter_no}")

        text = _normalize_whitespace(text)

        if not text:
            raise RuntimeError(f"Empty after translation: raw_id={raw_id}, ch={chapter_no}")

        # Return plain text only. No <p> tags.
        # Paragraph breaks are preserved as \n\n.
        return text

    def _retry_chapter_after_security_pause(
        self,
        raw_id: int,
        chapter_no: int,
        language: str,
    ) -> str:
        reason = (
            f"WTR-LAB returned a Turnstile/security-check page as chapter content: "
            f"raw_id={raw_id}, ch={chapter_no}."
        )

        for pause_attempt in range(1, self.security_pause_retries + 1):
            self._pause_for_security_check(
                reason + f" Pause retry {pause_attempt}/{self.security_pause_retries}."
            )

            reader = self._fetch_reader(
                raw_id=raw_id,
                chapter_no=chapter_no,
                language=language,
            )

            body = self._extract_body(reader)

            if not body:
                logger.warning(
                    "No body after security pause retry: raw_id=%s ch=%s attempt=%s/%s",
                    raw_id,
                    chapter_no,
                    pause_attempt,
                    self.security_pause_retries,
                )
                continue

            if self._is_encrypted(body):
                body = self._decrypt(body)

            text = self._to_plain_text(body)

            if text and not _RE_SECURITY_CHECK.search(text):
                return text

        raise RuntimeError(
            reason + " Still receiving security-check content after pause retries. "
            "Stopping to avoid saving bad .zst files."
        )

    def _fetch_reader(self, raw_id: int, chapter_no: int, language: str):
        root = self._site_root()
        url = f"{root}/api/reader/get"

        payload = {
            "translate": "web",
            "language": language,
            "raw_id": raw_id,
            "chapter_no": chapter_no,
        }

        return self._polite_json_request(
            "POST",
            url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers=self._headers(
                referer=self._chapter_referer(chapter_no),
                content_type="application/json",
            ),
            timeout=60,
        )

    def _apply_title(self, chapter, reader_json) -> None:
        chapter_data = reader_json.get("chapter") or {}
        title = chapter_data.get("title") or ""

        title = title.strip()
        if title:
            chapter.title = f"Chapter {chapter.id}: {title[0].upper()}{title[1:]}"

    @staticmethod
    def _looks_like_block_or_empty(reader_json) -> bool:
        if not isinstance(reader_json, dict):
            return False

        text = json.dumps(reader_json, ensure_ascii=False)[:5000]
        return bool(_RE_SECURITY_CHECK.search(text))

    # ------------------------------------------------------------------
    # Decrypt
    # ------------------------------------------------------------------

    def _decrypt(self, encrypted_body):
        resp = self.session.post(
            self.decrypt_proxy_url,
            json={"payload": encrypted_body},
            headers={
                "Content-Type": "application/json",
                "User-Agent": self.user_agent,
            },
            timeout=60,
        )
        resp.raise_for_status()

        data = resp.json()

        if isinstance(data, (list, str)):
            return data

        if isinstance(data, dict):
            for key in ("data", "body", "payload", "result", "content", "text", "html"):
                value = data.get(key)
                if value:
                    return value

        raise RuntimeError(f"Unexpected decrypt response: {data}")

    # ------------------------------------------------------------------
    # Translation
    # ------------------------------------------------------------------

    def _translate_zh_en(self, text: str) -> str:
        paragraphs = _split_paragraphs(text)

        if not paragraphs:
            return text

        translated = []

        for chunk in self._chunk_paragraphs(paragraphs, self.google_chunk_chars):
            result = self._translate_chunk(chunk)

            if not result:
                raise RuntimeError("Google translateHtml returned empty output")

            translated.extend(result)

            if self.google_chunk_delay > 0:
                time.sleep(self.google_chunk_delay)

        output = "\n\n".join(p.strip() for p in translated if p.strip())

        if not output:
            raise RuntimeError("Google translateHtml produced empty text")

        return output

    def _translate_chunk(self, paragraphs):
        # HTML is used only inside the Google request to preserve paragraph order.
        # The returned value is plain text.
        html_lines = [
            f'<p i="{i}">{html.escape(paragraph)}</p>' for i, paragraph in enumerate(paragraphs, 1)
        ]

        payload = [[html_lines, "zh-CN", "en"], "te_lib"]

        resp = self.session.post(
            self.translate_url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Accept": "*/*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json+protobuf",
                "Origin": "https://wtr-lab.com",
                "Referer": "https://wtr-lab.com/",
                "X-Goog-Api-Key": self.translate_api_key,
                "User-Agent": self.user_agent,
                "X-Browser-Channel": "stable",
                "X-Browser-Copyright": "Copyright 2026 Google LLC. All Rights Reserved.",
                "X-Browser-Validation": "jtgRBZiPXaTjtV6OwUZLvTDTXok=",
                "X-Browser-Year": "2026",
                "X-Client-Data": "CKmdygEIlKHLAQiFoM0B",
            },
            timeout=60,
        )

        resp.raise_for_status()

        strings = _collect_strings(resp.json())

        if not strings:
            raise RuntimeError(f"Unexpected translateHtml response: {resp.json()}")

        joined = _strip_html("\n\n".join(strings))
        return _split_paragraphs(_normalize_whitespace(joined))

    # ------------------------------------------------------------------
    # Body / text helpers
    # ------------------------------------------------------------------

    def _extract_body(self, data):
        if not isinstance(data, dict):
            return None

        for path in self._body_paths:
            node = data

            for key in path:
                if not isinstance(node, dict):
                    node = None
                    break

                node = node.get(key)

            if self._is_usable_body(node):
                return node

        return self._find_body_recursively(data)

    def _find_body_recursively(self, node):
        if self._is_usable_body(node):
            return node

        if isinstance(node, dict):
            priority_keys = ("body", "content", "text", "html", "payload", "result")

            for key in priority_keys:
                if key in node and self._is_usable_body(node[key]):
                    return node[key]

            for value in node.values():
                found = self._find_body_recursively(value)
                if found:
                    return found

        if isinstance(node, list):
            if node and all(isinstance(item, str) for item in node):
                joined = "\n\n".join(item.strip() for item in node if item.strip())
                if joined:
                    return joined

            for value in node:
                found = self._find_body_recursively(value)
                if found:
                    return found

        return None

    @staticmethod
    def _is_usable_body(value) -> bool:
        if isinstance(value, str):
            stripped = value.strip()
            return bool(stripped) and stripped not in ("[]", "{}", "null", "None")

        if isinstance(value, list):
            return any(str(item).strip() for item in value)

        return False

    def _to_plain_text(self, body) -> str:
        if isinstance(body, list):
            body = "\n\n".join(value for line in body if (value := str(line).strip()))

        if not isinstance(body, str):
            raise RuntimeError(f"Unexpected body type: {type(body).__name__}")

        text = body.strip()

        if _RE_HTML_TAG.search(text):
            text = _strip_html(text)

        text = _clean_disclaimers(text)
        return _normalize_whitespace(text)

    @staticmethod
    def _is_encrypted(body) -> bool:
        if isinstance(body, str):
            return body.startswith("arr:")

        if isinstance(body, list):
            return any(isinstance(item, str) and item.startswith("arr:") for item in body)

        return False

    @staticmethod
    def _looks_chinese(text: str) -> bool:
        return bool(text) and len(_RE_CHINESE_CHARS.findall(text)) >= 10

    def _chunk_paragraphs(self, paragraphs, max_chars: int):
        chunks = []
        current = []
        length = 0

        for paragraph in paragraphs:
            paragraph = paragraph.strip()

            if not paragraph:
                continue

            paragraph_length = len(paragraph)

            if paragraph_length > max_chars:
                if current:
                    chunks.append(current)
                    current = []
                    length = 0

                chunks.extend([piece] for piece in _split_long(paragraph, max_chars))
                continue

            if current and length + paragraph_length + 2 > max_chars:
                chunks.append(current)
                current = []
                length = 0

            current.append(paragraph)
            length += paragraph_length + 2

        if current:
            chunks.append(current)

        return chunks

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    def _site_root(self) -> str:
        url = self.novel_url or self.home_url or self.base_url[0]
        parsed = urlparse(url)
        return f"{parsed.scheme}://{parsed.netloc}"

    def _chapter_referer(self, chapter_no: int) -> str:
        parsed = urlparse(self.novel_url)
        path = re.sub(r"/chapter-\d+/?$", "", parsed.path)
        return f"{self._site_root()}{path}/chapter-{chapter_no}"

    @staticmethod
    def _language_from_url(url: str) -> str:
        parts = urlparse(url).path.strip("/").split("/")
        return parts[0] if parts and parts[0] else "en"

    @staticmethod
    def _attr_or_qs(chapter, key: str):
        value = getattr(chapter, key, None)

        if value is not None:
            return value

        values = parse_qs(urlparse(chapter.url).query).get(key)
        return values[0] if values else None


# ======================================================================
# Pure helpers
# ======================================================================


def _strip_html(text: str) -> str:
    """Convert HTML to plain text while preserving paragraph breaks."""
    text = re.sub(
        r"</(?:p|div|section|article|li|h\d|a)\s*>",
        "\n\n",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"<br\s*/?>", "\n", text, flags=re.IGNORECASE)
    text = re.sub(
        r"<(?:p|div|section|article|li|h\d|a)[^>]*>",
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = _RE_HTML_TAG.sub("", text)
    return _normalize_whitespace(html.unescape(text))


def _normalize_whitespace(text: str) -> str:
    """Normalize whitespace and repair common missing spaces after punctuation."""
    text = html.unescape(str(text))
    text = _RE_CR.sub("\n", text)
    text = _RE_TRAILING_WS.sub("\n", text)
    text = _RE_LEADING_WS.sub("\n", text)
    text = _RE_PUNCT_BEFORE_UPPER.sub(r"\1 ", text)
    text = _RE_PUNCT_BEFORE_LETTER.sub(r"\1 ", text)
    text = _RE_WHITESPACE_COLLAPSE.sub(" ", text)
    text = _RE_BLANK_LINES.sub("\n\n", text)
    return text.strip()


def _clean_disclaimers(text: str) -> str:
    text = html.unescape(text)
    text = _RE_DISCLAIMER_ZH.sub("", text)
    text = _RE_DISCLAIMER_EN.sub("", text)
    return text


def _split_paragraphs(text: str):
    return [paragraph.strip() for paragraph in _RE_PARAGRAPH_SPLIT.split(text) if paragraph.strip()]


def _split_long(text: str, max_chars: int):
    """Split oversized text at sentence-ish boundaries."""
    if len(text) <= max_chars:
        return [text]

    pieces = []
    start = 0

    while start < len(text):
        end = min(start + max_chars, len(text))
        split_at = max(text.rfind(ch, start, end) for ch in "。！？；.!?;\n")
        split_at = end if split_at <= start else split_at + 1

        piece = text[start:split_at].strip()
        if piece:
            pieces.append(piece)

        start = split_at

    return pieces


def _collect_strings(value) -> list[str]:
    """Walk nested JSON and return likely translated strings."""
    flat: list[str] = []

    def walk(node):
        if isinstance(node, str):
            stripped = node.strip()
            if stripped:
                flat.append(stripped)

        elif isinstance(node, list):
            for item in node:
                walk(item)

        elif isinstance(node, dict):
            for item in node.values():
                walk(item)

    walk(value)

    useful = [
        item
        for item in flat
        if any(tag in item.lower() for tag in ("<p", "</p>", "<a", "</a>", "<br"))
        or (len(item) > 2 and len(_RE_CHINESE_CHARS.findall(item)) < 10)
    ]

    return useful or flat
