# -*- coding: utf-8 -*-
import base64
import json
import logging
import math
from typing import List, Union

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import requests

from lncrawl.core import Chapter, LegacyCrawler, SearchResult

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

        query = metadata["query"]
        page_props = metadata["props"]["pageProps"]
        series_data = page_props["serie"]["serie_data"]
        clean_url = self.novel_url.split("?")[0].strip("/")

        self.novel_cover = series_data["data"]["image"]
        self.novel_title = series_data["data"]["raw"]["title"]
        self.novel_author = series_data["data"]["raw"]["author"]
        self.novel_synopsis = series_data["data"]["raw"]["description"]
        if "tags" in page_props:
            self.novel_tags = [tag["title"] for tag in page_props["tags"] if tag.get("title")]

        # self.language = query["locale"] # reports wrong language for raws

        raw_id = query["raw_id"]
        chapter_count = series_data["chapter_count"]
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
            for item in page["chapters"]:
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

    def download_chapter_body(self, chapter):
        url = f"{self.scraper.origin}/api/reader/get"
        payload = json.dumps(
            {
                # "translate": "ai", # note: disabled as it requires login
                "language": chapter.language,
                "raw_id": chapter.serie_id,
                "chapter_no": chapter.order,
                "retry": False,
                "force_retry": False,
                "chapter_id": chapter.chapter_id,
            }
        )
        headers = {"Content-Type": "application/json"}
        jsonData = self.get_json(url, data=payload, headers=headers)
        if not jsonData["success"]:
            raise Exception(jsonData["error"])
        body = jsonData["data"]["data"]["body"]

        content = ""
        for line in self.decrypt_body(body):
            content += f"<p>{line}</p>"
        return content

    def decrypt_body(self, encrypted: Union[str, List[str]]):
        # search for "Invalid encrypted data format" or "AES-GCM"
        KEY = b"IJAFUUxjM25hyzL2AZrn0wl7cESED6Ru"
        is_array = False

        if isinstance(encrypted, list):
            return encrypted
        elif not isinstance(encrypted, str):
            raise ValueError("Unknown chapter content type")

        if encrypted.startswith("arr:"):
            is_array = True
            encrypted = encrypted[4:]
        elif encrypted.startswith("str:"):
            encrypted = encrypted[4:]
        else:
            raise ValueError("Unknown chapter content format")

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
