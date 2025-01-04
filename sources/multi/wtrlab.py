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
        self.novel_tags = [
            tag["title"]
            for tag in metadata["props"]["pageProps"]["tags"]
            if tag.get("title")
        ]
        self.language = urlparse(self.novel_url).path.split("/")[0]

        serie_id = series_data["raw_id"]
        for idx, chapter in enumerate(series["chapters"]):
            chap_id = 1 + idx
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            url = f"{self.home_url}{self.language}/serie-{serie_id}/{novel_slug}/chapter-{chapter['order']}"
            if chap_id % 100 == 1:
                self.volumes.append(Volume(id=vol_id, title=vol_title))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=url,
                    title=chapter["title"],
                    volume=vol_id,
                    volume_title=vol_title,
                ),
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        chapter_metadata = soup.select_one("script#__NEXT_DATA__")
        chapter_json = json.loads(chapter_metadata.text)
        assert chapter_json

        series_data = chapter_json["props"]["pageProps"]["serie"]

        # adjust chapter title as the one from the overview usually lacks details
        details = series_data["chapter"]
        chapter.title = f"#{details['slug']}: {details['title']}"

        text_lines = series_data["chapter_data"]["data"]["body"]
        return "".join(
            [
                f"<p>{t.strip()}</p>"
                for t in text_lines
                if not self.cleaner.contains_bad_texts(t)
            ]
        )
