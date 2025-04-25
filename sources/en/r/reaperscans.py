# -*- coding: utf-8 -*-
import logging
from lxml import etree
import json
import base64
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

CHAPTER_LIST_URL = (
    "https://api.reaperscans.com/chapters/{}?page={}&perPage=100&order=asc"
)
NOVEL_URL = "https://api.reaperscans.com/series/{}"

INIT_PATTERN = re.compile(
    r"\(self\.__next_f\s?=\s?self\.__next_f\s?\|\|\s?\[\]\)\.push\((\[.+?\])\)"
)
PAYLOAD_PATTERN = re.compile(r"self\.__next_f\.push\((\[.+)\)$")
TEXT_PATTERN = re.compile(r"^[a-fA-F0-9]+:T(.*)", re.DOTALL)
HEX_PREFIX_PATTERN = re.compile(r"^([0-9a-fA-F]+),\n")
ID_MARKER_PATTERN = re.compile(r"\n(?=[a-fA-F0-9]+:)")


class Reaperscans(Crawler):
    base_url = "https://reaperscans.com/"

    def initialize(self):
        self.cleaner.bad_text_regex = set(
            [
                "Translator",
                "Proofreader",
                "Reaper Scans",
                "REAPER SCANS",
                "https://dsc.gg/reapercomics",
                "https://discord.gg/MaRegMFhRb",
                "https://discord.gg/reapercomics",
                "h ttps://discord.gg/reapercomic",
                "https://discord.gg/sb2jqkv",
                "____",
                "Join our Discord",
            ]
        )
        self.init_executor(ratelimit=0.9)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)

        novel_slug = urlparse(self.novel_url).path.split("/")[2]
        data = self.get_json(NOVEL_URL.format(novel_slug))

        self.novel_id = data["id"]
        logger.info("Novel ID: %d", self.novel_id)

        self.novel_title = data["title"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = data["thumbnail"]
        logger.info("Novel cover: %s", self.novel_cover)

        chapters = []
        data = self.get_json(CHAPTER_LIST_URL.format(self.novel_id, 1))
        chapters += data["data"]

        futures = []
        for page in range(2, data["meta"]["last_page"] + 1):
            url = CHAPTER_LIST_URL.format(self.novel_id, page)
            futures.append(self.executor.submit(self.get_json, url))

        for f in futures:
            data = f.result()
            chapters += data["data"]

        for item in chapters:
            chap_id = 1 + (len(self.chapters))
            chap_name = item["chapter_name"]
            self.chapters.append(
                {
                    "id": chap_id,
                    "url": f"{self.novel_url}/{item['chapter_slug']}",
                    "title": chap_name if chap_name else item["chapter_title"],
                }
            )

    def extract_nextjs_flight_text(self, html: str) -> str:
        """
        Extracts text content from Next.js flight data in HTML.
        """
        tree = etree.HTML(html)
        scripts = tree.xpath("//script/text()")

        raw_chunks = []
        for script in filter(None, scripts):
            for line in script.strip().splitlines():
                for pattern in (INIT_PATTERN, PAYLOAD_PATTERN):
                    match = pattern.search(line)
                    if match and match.group(1):
                        try:
                            raw_chunks.append(json.loads(match.group(1)))
                            break
                        except json.JSONDecodeError:
                            pass

        if not raw_chunks:
            return ""

        decoded_data = []
        for chunk in raw_chunks:
            if not isinstance(chunk, list) or len(chunk) < 2:
                continue

            typ, val = chunk[0], chunk[1]
            if not isinstance(val, str):
                continue

            # Add string directly or decode base64
            if typ == 1:
                decoded_data.append(val)
            elif typ == 3:
                try:
                    decoded_data.append(
                        base64.b64decode(val).decode("utf-8", errors="replace")
                    )
                except (base64.binascii.Error, UnicodeDecodeError):
                    pass

        if not decoded_data:
            return ""

        combined = "\n".join(decoded_data)
        segments = []

        for line in ID_MARKER_PATTERN.split(combined):
            match = TEXT_PATTERN.match(line)
            if match:
                content = match.group(1)
                # Remove hex length prefix if present
                hex_match = HEX_PREFIX_PATTERN.match(content)
                if hex_match:
                    content = content[hex_match.end() :]
                segments.append(content)

        return segments

    def download_chapter_body(self, chapter):
        response = self.get_response(chapter["url"], timeout=10)
        html_text = response.content.decode("utf8", "ignore")
        content = self.extract_nextjs_flight_text(html_text)[0]
        chapter_body = BeautifulSoup(content, "lxml")
        return self.cleaner.extract_contents(chapter_body)
