# -*- coding: utf-8 -*-
import logging
import json
import re

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

    base_url = ["https://wtr-lab.com/"]
    has_manga = False
    has_mtl = True
    host = ""

    def initialize(self) -> None:
        self.host = self.home_url[:-1] if self.home_url.endswith("/") else self.home_url

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        metadata_json = soup.select_one('script#__NEXT_DATA__')
        metadata = json.loads(metadata_json.text)
        assert metadata  # this is where we get everything so it's kinda required

        novel_slug = metadata['props']['pageProps']['serie']['serie_data']['slug']
        self.novel_title = metadata['props']['pageProps']['serie']['serie_data']['data']['title']
        self.novel_cover = metadata['props']['pageProps']['serie']['serie_data']['data']['image']
        try:
            self.novel_tags = [tag["title"] for tag in metadata['props']['pageProps']['tags']]
        except KeyError:
            # worst case we miss out on tags
            pass
        self.novel_synopsis = metadata['props']['pageProps']['serie']['serie_data']['data']['description']
        self.novel_author = metadata['props']['pageProps']['serie']['serie_data']['data']['author']

        logger.info("book metadata %s", metadata)

        # examples:
        lang = re.match(f"{self.host}(/?.*)/serie-\\d+/.+/?", self.novel_url).group(1)
        # lang will be something like "/en" or "/es"
        self.language = lang[1:]
        serie_id = metadata['props']['pageProps']['serie']['serie_data']['raw_id']

        for idx, chapter in enumerate(metadata['props']['pageProps']['serie']['chapters']):
            chap_id = 1 + idx
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            url = f"{self.host}{lang}/serie-{serie_id}/{novel_slug}/chapter-{chapter['order']}"
            if chap_id % 100 == 1:
                self.volumes.append(
                    Volume(
                        id=vol_id,
                        title=vol_title
                    ))

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=url,
                    title=chapter["title"],
                    volume=vol_id,
                    volume_title=vol_title
                ),
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        chapter_metadata = soup.select_one("script#__NEXT_DATA__")
        chapter_json = json.loads(chapter_metadata.text)
        assert chapter_json

        logger.info("chapeter %s", chapter_json)
        chapter_details = chapter_json['props']['pageProps']['serie']['chapter']
        # adjust chapter title as the one from the overview usually lacks details
        chapter.title = chapter_details['code'] + " " + chapter_details['title']
        # get all text
        text_lines = chapter_json['props']['pageProps']['serie']['chapter_data']['data']['body']

        # copied straight outta self.cleaner.extract_contents because we lack a TAG...
        # otherwise the output looks very mushed together cause it ignores all the newlines otherwise
        text = "".join(
            [
                f"<p>{t.strip()}</p>"
                for t in text_lines
                if not self.cleaner.contains_bad_texts(t)
            ]
        )

        return text

    def search_novel(self, query: str):
        novels = requests.post(f"{self.host}/api/search", json={"text": query}).json()
        logger.info("Search results: %s", novels)

        for novel in novels["data"]:
            data = novel["data"]
            meta = {
                "Chapters": novel["chapter_count"],
                "Status": self.status_idx_to_text(novel["status"]),
                "Author": data["author"]

            }
            info = " | ".join(f"{k}: {v}" for k, v in meta.items())

            yield SearchResult(
                title=data["title"],
                # default to EN
                url=f"{self.host}/en/serie-{novel['raw_id']}/f{novel['slug']}",
                info=info
            )
        return []

    @staticmethod
    def status_idx_to_text(idx):
        return "Ongoing" if idx else "Completed"

    @staticmethod
    def premium_idx_to_text(idx):
        if idx == 2:
            return "Partial Paywall"
        else:
            return "Unknown"
