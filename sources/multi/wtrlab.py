# -*- coding: utf-8 -*-
import json
import logging
from urllib.parse import urlparse

import requests

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult, Volume

logger = logging.getLogger(__name__)


class WtrLab(Crawler):
    """
    This site has multilingual novels, basically all MTL, supposedly through translators like Google
    but the output seems pretty decent for that
    The whole site obfuscates classes via Angular or some type of minifier
    so the only constant HTML comes from display text & HTML IDs
    But luckily all necessary data is stored in a consistent JSON that's always in the same script tag
    Essentially the same framework as webfic though with some other keys, urls, etc.
    """

    base_url = ["https://wtr-lab.com"]
    has_mtl = True

    def search_novel(self, query: str):
        novels = requests.post(
            "https://www.wtr-lab.com/api/search",
            json={"text": query},
        ).json()
        logger.info("Search results: %s", novels)

        for novel in novels["data"]:
            data = novel["data"]
            meta = {
                "Chapters": novel["chapter_count"],
                "Author": data["author"],
                "Status": "Ongoing" if novel["status"] else "Completed",
            }
            yield SearchResult(
                title=data["title"],
                url=f"https://www.wtr-lab.com/en/serie-{novel['raw_id']}/f{novel['slug']}",
                info=" | ".join(f"{k}: {v}" for k, v in meta.items()),
            )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        metadata_json = soup.select_one("script#__NEXT_DATA__")
        metadata = json.loads(metadata_json.text)

        series = metadata["props"]["pageProps"]["serie"]
        series_data = series["serie_data"]

        self.novel_title = series_data["data"]["title"]
        self.novel_cover = series_data["data"]["image"]
        self.novel_synopsis = series_data["data"]["description"]
        self.novel_author = series_data["data"]["author"]

        # Check if "tags" exists; if not, use the "genres" field as a fallback.
        if "tags" in metadata["props"]["pageProps"]:
            self.novel_tags = [
                tag["title"]
                for tag in metadata["props"]["pageProps"]["tags"]
                if tag.get("title")
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
        url = f"{self.home_url}/api/reader/get"
        payload = json.dumps({
            "language": "en",
            "raw_id": int(chapter.url),
            "chapter_no": chapter.id,
        })
        headers = {"Content-Type": "application/json"}
        jsonData = self.get_json(url, data=payload, headers=headers)
        title = jsonData["chapter"]["title"]
        chapter.title = f"Chapter {chapter.id}: {str(title[0]).upper() + title[1:]}"
        body = jsonData["data"]["data"]["body"]
        chapterText = ""
        for line in body:
            chapterText += f"<p>{line}</p>"
        return chapterText
