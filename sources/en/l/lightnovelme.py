# -*- coding: utf-8 -*-
import json
import logging
from urllib.parse import quote

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = "https://lightnovels.me/api/search?keyword=%s&index=0&limit=20"
chapter_list_url = "https://lightnovels.me/api/chapters?id=%d&index=1&limit=15000"


class LightnovelMe(Crawler):
    base_url = ["https://lightnovels.me/"]

    def search_novel(self, query):
        data = self.get_json(search_url % quote(query))

        results = []
        for item in data["results"]:
            results.append(
                {
                    "title": item["novel_name"],
                    "url": "https://lightnovels.me/novel" + item["novel_slug"],
                    "info": f"Status: {item['status']} | Latest: {item['chapter_name']}",
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        script = soup.select_one("script#__NEXT_DATA__")
        assert isinstance(script, Tag)
        data = json.loads(script.text)

        novel_info = data["props"]["pageProps"]["novelInfo"]
        novel_id = novel_info["novel_id"]
        self.novel_title = novel_info["novel_name"]
        self.novel_cover = self.absolute_url(novel_info["novel_image"])
        self.novel_author = ", ".join(
            [x["name"] for x in data["props"]["pageProps"]["authors"]]
        )

        data = self.get_json(chapter_list_url % (novel_id))

        for i, item in enumerate(data["results"]):
            chap_id = i + 1
            vol_id = i // 100 + 1
            if i % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": item["chapter_name"],
                    "url": self.absolute_url(item["slug"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        script = soup.select_one("script#__NEXT_DATA__")
        assert isinstance(script, Tag)
        data = json.loads(script.text)

        chapter_info = data["props"]["pageProps"]["cachedChapterInfo"]
        content = str(chapter_info["content"])
        content = content.replace("\u003c", "<").replace("\u003e", ">")
        content = content.replace("<p>" + chapter_info["chapter_name"] + "</p>", "", 1)
        return content
