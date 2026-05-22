# -*- coding: utf-8 -*-
import base64
import json
import logging
from urllib.parse import urlparse

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import requests

from lncrawl.core import Chapter, LegacyCrawler, SearchResult, Volume

logger = logging.getLogger(__name__)


class WtrLab(LegacyCrawler):
    base_url = ["https://wtr-lab.com"]
    has_mtl = True

    def initialize(self) -> None:
        super().initialize()
        self.init_executor(workers=2)

    def search_novel(self, query: str):
        novels = requests.post(
            "https://www.wtr-lab.com/api/search",
            json={"text": query},
        ).json()
        logger.info("Search results: %s", novels)

        results = []
        for novel in novels["data"]:
            data = novel["data"]
            meta = {
                "Chapters": novel["chapter_count"],
                "Author": data["author"],
                "Status": "Ongoing" if novel["status"] else "Completed",
            }
            url = f"https://www.wtr-lab.com/en/serie-{novel['raw_id']}/f{novel['slug']}"
            results.append(
                SearchResult(
                    url=url,
                    title=data["title"],
                    info=" | ".join(f"{k}: {v}" for k, v in meta.items()),
                )
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        metadata_json = soup.select_one("script#__NEXT_DATA__")
        assert metadata_json, "No next data found"
        metadata = json.loads(metadata_json.get_text(strip=True))

        series = metadata["props"]["pageProps"]["serie"]
        series_data = series["serie_data"]

        self.novel_title = series_data["data"]["title"]
        self.novel_cover = series_data["data"]["image"]
        self.novel_synopsis = series_data["data"]["description"]
        self.novel_author = series_data["data"]["author"]

        # Check if "tags" exists; if not, use the "genres" field as a fallback.
        if "tags" in metadata["props"]["pageProps"]:
            self.novel_tags = [
                tag["title"] for tag in metadata["props"]["pageProps"]["tags"] if tag.get("title")
            ]
        else:
            # Convert numeric genre IDs to strings (or use a mapping if available)
            self.novel_tags = list(map(str, series_data.get("genres", [])))

        self.language = urlparse(self.novel_url).path.split("/")[0]

        raw_id = series_data["raw_id"]
        chapter_count = series_data["chapter_count"]
        for idx in range(chapter_count):
            chap_id = idx + 1
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            chapter_title = f"Chapter {chap_id}"

            if chap_id % 100 == 1:
                self.volumes.append(Volume(id=vol_id, title=vol_title))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=raw_id,
                    title=chapter_title,
                    volume=vol_id,
                    volume_title=vol_title,
                )
            )

    def download_chapter_body(self, chapter):
        url = f"{self.scraper.origin}/api/reader/get"
        payload = json.dumps(
            {
                "language": "en",
                "raw_id": int(chapter.url),
                "chapter_no": chapter.id,
            }
        )
        headers = {"Content-Type": "application/json"}
        jsonData = self.get_json(url, data=payload, headers=headers)
        title = jsonData["chapter"]["title"]
        chapter.title = f"Chapter {chapter.id}: {str(title[0]).upper() + title[1:]}"
        encrypted = jsonData["data"]["data"]["body"]
        body = self.decrypt_body(encrypted)

        chapterText = ""
        for line in body:
            chapterText += f"<p>{line}</p>"
        return chapterText

    def decrypt_body(self, encrypted: str):
        # search for "Invalid encrypted data format" or "AES-GCM"
        KEY = b"IJAFUUxjM25hyzL2AZrn0wl7cESED6Ru"
        is_array = False

        if encrypted.startswith("arr:"):
            is_array = True
            encrypted = encrypted[4:]
        elif encrypted.startswith("str:"):
            encrypted = encrypted[4:]

        parts = encrypted.split(":")
        if len(parts) != 3:
            raise ValueError("Invalid encrypted data format")

        s, n, a = parts
        iv = base64.b64decode(s)
        n_bytes = base64.b64decode(n)
        a_bytes = base64.b64decode(a)

        # JS builds: d = [...a_bytes, ...n_bytes]  (ciphertext then auth tag)
        ciphertext_and_tag = a_bytes + n_bytes

        plaintext = AESGCM(KEY).decrypt(iv, ciphertext_and_tag, None)
        decoded = plaintext.decode("utf-8")

        return json.loads(decoded) if is_array else decoded
