
# -*- coding: utf-8 -*-

import base64
import json
import logging
import math
import re
from typing import List, Union
from urllib.parse import unquote, urljoin

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from scraper import Action, Blocked, Diagnosis
from lncrawl.core import Chapter, LegacyCrawler, PageSoup, SearchResult

logger = logging.getLogger(__name__)


class WtrLab(LegacyCrawler):
    base_url = ["https://wtr-lab.com"]
    has_mtl = True
    request_rate_limit = 1

    def check_response(self, response, body: str):
        if '"requireTurnstile"' not in body:
            return None

        try:
            data = json.loads(body)
        except ValueError:
            return None

        if data.get("success") or not data.get("requireTurnstile"):
            return None

        detail = "this address is past the chapters it is allowed"

        if data.get("count") and data.get("threshold"):
            detail += f" ({data['count']} of {data['threshold']})"

        return Diagnosis(Action.ROTATE, None, detail)

    def _parse_next_data(self, soup: PageSoup):
        script = soup.select_one("script#__NEXT_DATA__")

        if not script:
            raise ValueError("WTR-Lab: __NEXT_DATA__ script not found")

        return json.loads(script.get_text(strip=True))

    def search_novel(self, query: str):
        novels = self.post_json(
            "https://www.wtr-lab.com/api/search",
            json={"text": query},
        )

        results = []

        for novel in novels.get("data", []):
            data = novel.get("data", {})
            raw_id = novel.get("raw_id")
            slug = novel.get("slug", "")

            meta = {
                "Chapters": novel.get("chapter_count", "?"),
                "Author": data.get("author", "Unknown"),
                "Status": (
                    "Ongoing" if novel.get("status") else "Completed"
                ),
            }

            results.append(
                SearchResult(
                    url=(
                        f"https://www.wtr-lab.com/en/"
                        f"serie-{raw_id}/f{slug}"
                    ),
                    title=data.get("title", "Unknown Title"),
                    info=" | ".join(
                        f"{key}: {value}"
                        for key, value in meta.items()
                    ),
                )
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        metadata = self._parse_next_data(soup)

        query = metadata.get("query", {})
        page_props = metadata.get("props", {}).get(
            "pageProps", {}
        )

        serie = page_props.get("serie", {})
        series_data = serie.get("serie_data", {})
        data = series_data.get("data", {})
        raw = data.get("raw", {})

        title = (
            raw.get("title")
            or data.get("title")
            or serie.get("title")
            or series_data.get("title")
        )

        author = (
            raw.get("author")
            or data.get("author")
            or serie.get("author")
        )

        description = (
            raw.get("description")
            or data.get("description")
            or serie.get("description")
            or ""
        )

        self.novel_cover = (
            data.get("image")
            or raw.get("image")
            or serie.get("image")
            or ""
        )

        if not title:
            slug = (
                self.novel_url.split("?")[0]
                .rstrip("/")
                .rsplit("/", 1)[-1]
            )
            title = unquote(slug).replace("-", " ").title()

        if not title:
            raise ValueError("WTR-Lab: Novel title not found")

        self.novel_title = title
        self.novel_author = author or "Unknown Author"
        self.novel_synopsis = description

        if "tags" in page_props:
            self.novel_tags = [
                tag["title"]
                for tag in page_props["tags"]
                if tag.get("title")
            ]

        raw_id = query.get("raw_id")

        match = re.search(r"/novel/(\d+)", self.novel_url)
        if not raw_id and match:
            raw_id = int(match.group(1))

        if not raw_id:
            match = re.search(r"/serie-(\d+)", self.novel_url)
            if match:
                raw_id = int(match.group(1))

        if not raw_id:
            raise ValueError("WTR-Lab: Novel ID not found")

        chapter_count = (
            series_data.get("chapter_count")
            or serie.get("chapter_count")
            or page_props.get("chapter_count")
            or 0
        )

        if not chapter_count:
            raise ValueError("WTR-Lab: Chapter count not found")

        clean_url = self.novel_url.split("?")[0].rstrip("/")
        batch_size = 250
        batch_count = math.ceil(chapter_count / batch_size)

        batches = [
            (
                1 + batch * batch_size,
                min(chapter_count, (batch + 1) * batch_size),
            )
            for batch in range(batch_count)
        ]

        toc_url = f"{self.scraper.origin}api/chapters/{raw_id}"
        headers = {"Content-Type": "application/json"}

        futures = [
            self.taskman.submit_task(
                self.get_json,
                f"{toc_url}?start={start}&end={end}",
                headers=headers,
            )
            for start, end in batches
        ]

        for page in self.taskman.resolve_futures(
            futures,
            desc="Chapters",
            unit="batch",
            fail_fast=True,
        ):
            for item in page.get("chapters", []):
                self.chapters.append(
                    Chapter(
                        id=item["order"],
                        title=item["name"],
                        en_title=item["title"],
                        order=item["order"],
                        language=self.language,
                        chapter_id=item["id"],
                        serie_id=item["serie_id"],
                        url=f"{clean_url}/chapter-{item['order']}",
                    )
                )

    def _find_encrypted_payload(self, value, depth=0):
        """Find the encrypted chapter payload in an API response."""

        if depth > 8:
            return None

        if isinstance(value, str):
            stripped = value.strip()

            if stripped.startswith(("str:", "arr:")):
                return stripped

            # Some endpoints may return JSON encoded as text.
            if stripped.startswith(("{", "[", '"')):
                try:
                    parsed = json.loads(stripped)
                    if parsed != value:
                        return self._find_encrypted_payload(
                            parsed, depth + 1
                        )
                except (ValueError, TypeError):
                    pass

            return None

        if isinstance(value, list):
            # A list may already be the decoded chapter paragraphs.
            if all(isinstance(item, str) for item in value):
                return value

            for item in value:
                found = self._find_encrypted_payload(
                    item, depth + 1
                )
                if found is not None:
                    return found

            return None

        if isinstance(value, dict):
            # Check likely content fields first.
            for key in (
                "body",
                "content",
                "encrypted",
                "encrypted_data",
                "content_data",
                "text",
                "data",
                "result",
            ):
                if key in value:
                    found = self._find_encrypted_payload(
                        value[key], depth + 1
                    )
                    if found is not None:
                        return found

            return None

        return None

    def download_chapter_body(self, chapter):
        reader_url = urljoin(
            self.scraper.origin,
            "/api/reader/get",
        )

        payload = json.dumps(
            {
                "translate": "web",
                "language": chapter.language,
                "raw_id": chapter.serie_id,
                "chapter_no": chapter.order,
                "retry": False,
                "force_retry": False,
                "chapter_id": chapter.chapter_id,
            }
        )

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json, text/javascript, */*",
        }

        reader_data = self.get_json(
            reader_url,
            data=payload,
            headers=headers,
        )

        if not isinstance(reader_data, dict):
            raise ValueError(
                "WTR-Lab reader returned an unexpected response type"
            )

        if not reader_data.get("success"):
            raise Blocked(
                None,
                str(reader_data.get("message", reader_data)),
                reader_url,
            )

        # NEW API: the reader response supplies content_url.
        content_url = reader_data.get("content_url")

        if not content_url:
            # Compatibility fallback for the old response format.
            encrypted = self._find_encrypted_payload(reader_data)

            if encrypted is None:
                raise ValueError(
                    "WTR-Lab: No content_url or encrypted body found. "
                    f"Response keys: {list(reader_data.keys())}"
                )

            content = self.decrypt_body(encrypted)
            return self._format_chapter_content(content)

        content_url = urljoin(reader_url, content_url)

        logger.info(
            "Fetching WTR-Lab chapter content from %s",
            content_url,
        )

        # Fetch the actual chapter content from the new endpoint.
        response = self.get_response(
            content_url,
            headers={
                "Accept": "application/json, text/plain, */*"
            },
        )
        response.raise_for_status()

        # The endpoint may return JSON or plain text.
        try:
            content_response = response.json()
        except (ValueError, json.JSONDecodeError):
            content_response = response.text

        encrypted = self._find_encrypted_payload(content_response)

        if encrypted is None:
            preview = (
                content_response
                if isinstance(content_response, str)
                else json.dumps(
                    content_response,
                    ensure_ascii=False,
                )
            )

            raise ValueError(
                "WTR-Lab content endpoint returned no recognized "
                "encrypted payload. "
                f"HTTP status: {response.status_code}. "
                f"Content type: "
                f"{response.headers.get('content-type', 'unknown')}. "
                f"Response preview: {preview[:1200]}"
            )

        # Decrypt only after locating the actual payload.
        content = self.decrypt_body(encrypted)

        return self._format_chapter_content(content)

    def _format_chapter_content(self, content):
        """Convert decrypted chapter paragraphs to HTML."""

        if isinstance(content, str):
            lines = content.splitlines()
        elif isinstance(content, list):
            lines = content
        else:
            raise ValueError(
                "WTR-Lab: Decrypted chapter has an unsupported type: "
                f"{type(content).__name__}"
            )

        paragraphs = []

        for line in lines:
            if line is None:
                continue

            text = str(line).strip()

            if text:
                # Escape HTML-sensitive characters in plain text.
                text = (
                    text.replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                paragraphs.append(f"<p>{text}</p>")

        return "\n".join(paragraphs)

    def decrypt_body(self, encrypted: Union[str, List[str]]):
        KEY = b"IJAFUUxjM25hyzL2AZrn0wl7cESED6Ru"

        if isinstance(encrypted, list):
            return encrypted

        if not isinstance(encrypted, str):
            raise ValueError(
                "WTR-Lab: Unknown chapter content type"
            )

        if encrypted.startswith("arr:"):
            is_array = True
            encrypted = encrypted[4:]
        elif encrypted.startswith("str:"):
            is_array = False
            encrypted = encrypted[4:]
        else:
            raise ValueError(
                "WTR-Lab: Content is not in the expected "
                "str:/arr: encrypted format"
            )

        parts = encrypted.split(":")

        if len(parts) != 3:
            raise ValueError(
                "WTR-Lab: Invalid encrypted data format"
            )

        s, n, a = parts

        iv = base64.b64decode(s)
        n_bytes = base64.b64decode(n)
        a_bytes = base64.b64decode(a)

        # Preserve the original WTR-Lab AES-GCM payload ordering.
        ciphertext_and_tag = a_bytes + n_bytes

        plaintext = AESGCM(KEY).decrypt(
            iv,
            ciphertext_and_tag,
            None,
        )

        decoded = plaintext.decode("utf-8")

        return json.loads(decoded) if is_array else decoded
