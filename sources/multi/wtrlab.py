# -*- coding: utf-8 -*-
import json
import logging
from urllib.parse import urlparse

import requests

from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter, SearchResult

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

    base_url = "https://wtr-lab.com"
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

        novel_slug = series_data["slug"]
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

        serie_id = series_data["raw_id"]
        chapter_count = series_data["chapter_count"]
        for idx in range(chapter_count):
            chap_id = idx + 1
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            url = f"{self.home_url}{self.language}/serie-{serie_id}/{novel_slug}/chapter-{chap_id}"
            chapter_title = f"Chapter {chap_id}"

            if chap_id % 100 == 1:
                self.volumes.append(Volume(id=vol_id, title=vol_title))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=url,
                    title=chapter_title,
                    volume=vol_id,
                    volume_title=vol_title,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)
        chapter_metadata = soup.select_one("script#__NEXT_DATA__")
        chapter_json = json.loads(chapter_metadata.text)
        assert chapter_json

        page_props = chapter_json["props"]["pageProps"]
        # The chapter details now reside in the "chapter" key.
        if "chapter" in page_props:
            chapter_data = page_props["chapter"]["data"]
            chapter.title = f"#{chapter_data.get('slug', chapter.title)}: {chapter_data.get('title', chapter.title)}"
            text_lines = chapter_data.get("body", [])
        else:
            series_data = page_props["serie"]
            details = series_data.get("chapter", {})
            chapter.title = f"#{details.get('slug', chapter.title)}: {details.get('title', chapter.title)}"
            text_lines = series_data.get("chapter_data", {}).get("data", {}).get("body", [])

        return "".join(
            [
                f"<p>{t.strip()}</p>"
                for t in text_lines
                if not self.cleaner.contains_bad_texts(t)
            ]
        )
