# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

import json

logger = logging.getLogger(__name__)
data_url = "https://novelsala.com/_next/data/%s/en%s"
search_url = "https://novelsala.com/search/?q=%s"

graphql_url = "https://novelsala.com/graphql"
graphql_body = """{"id":"chapters_NovelRefetchQuery","query":"query chapters_NovelRefetchQuery(\\n  $slug: String!\\n  $startChapNum: Int\\n) {\\n  ...chapters_list_items\\n}\\n\\nfragment chapters_list_items on Query {\\n  chapterListChunks(bookSlug: $slug, chunkSize: 100, startChapNum: $startChapNum) {\\n    items {\\n      title\\n      chapNum\\n      url\\n      refId\\n      id\\n    }\\n    title\\n    startChapNum\\n  }\\n}\\n","variables":{"slug":"%s","startChapNum":%d}}"""  # noqa: E501


class NovelSalaCrawler(Crawler):
    base_url = ["https://novelsala.com/"]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select("a.cell-active"):
            title = a.select_one(".body h3").text
            info = a.select_one(".body span").text
            results.append(
                {
                    "title": title,
                    "url": self.home_url.rstrip("/") + a["href"],
                    "info": info,
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        script_data = soup.select_one('script[id="__NEXT_DATA__"]').get_text()
        json_data = json.loads(script_data)

        buildId = json_data["buildId"]
        book_data = json_data["props"]["pageProps"]["relayData"][0][1]["data"]["book"][
            "edges"
        ][0]["node"]

        self.novel_title = book_data["title"]
        self.novel_cover = book_data["coverLg"]
        self.novel_author = book_data["author"]["name"]

        logger.info("Novel author: %s", self.novel_author)

        slug = book_data["slug"]

        volume_chapters = self.post_json(graphql_url, data=graphql_body % (slug, 1))[
            "data"
        ]["chapterListChunks"]

        for vol_id, volume in enumerate(volume_chapters, 1):
            if vol_id != 1:
                volume = (
                    self.post_json(
                        graphql_url, data=graphql_body % (slug, volume["startChapNum"])
                    )["data"]["chapterListChunks"]
                )[vol_id - 1]

            self.volumes.append({"id": vol_id})

            for chapter in volume["items"]:
                self.chapters.append(
                    {
                        "id": chapter["chapNum"],
                        "volume": vol_id,
                        "title": f"Chapter {chapter['chapNum']}: " + chapter["title"],
                        "url": self.home_url.rstrip("/") + chapter["url"],
                        "json_url": (
                            data_url % (buildId, book_data["url"])
                            + f"chapter-{chapter['chapNum']}.json"
                        ),
                    }
                )

    def download_chapter_body(self, chapter):
        chapter_json = self.get_json(chapter["json_url"])
        chapter_data = chapter_json["pageProps"]["relayData"][0][1]["data"]["chapter2"]

        return chapter_data["contentHtml"]
