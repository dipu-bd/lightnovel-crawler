# -*- coding: utf-8 -*-
import json
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class TeaNovelCrawler(Crawler):
    base_url = ["https://www.teanovel.com/", "https://www.teanovel.net/"]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        script_tag = soup.select_one("script#__NEXT_DATA__")
        if not isinstance(script_tag, Tag):
            raise LNException("No script data found")

        next_data = json.loads(script_tag.get_text())

        build_id = next_data["buildId"]
        novel_data = next_data["props"]["pageProps"]["novelData"]["novel"]

        self.novel_title = novel_data["name"]
        self.novel_author = novel_data["author"]

        # img_tag = soup.select_one("main img[src*='_next/']")
        # if isinstance(img_tag, Tag):
        #     self.novel_cover = self.absolute_url(img_tag["src"])

        slug = novel_data["slug"]

        toc_url = f"{self.home_url}api/chapters/{slug}?slug={slug}&orderBy=asc"
        toc_json = self.get_json(toc_url)

        while True:
            for chapter in toc_json["data"]:
                chapter_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chapter_id,
                        "title": f"Chapter {chapter_id}: {chapter['title']}",
                        "url": (
                            f"{self.home_url}_next/data/{build_id}/novel/{slug}/{chapter['slug']}.json"
                        ),
                    }
                )
            if "nextId" in toc_json:
                toc_json = self.get_json(toc_url + f"&nextId={toc_json['nextId']}")
            else:
                break

    def download_chapter_body(self, chapter):
        chapter_json = self.get_json(chapter["url"])
        chapter_data = chapter_json["pageProps"]["chapterData"]

        return chapter_data["content"].replace("\n", "<br>")
