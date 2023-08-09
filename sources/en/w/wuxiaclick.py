# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
import json

logger = logging.getLogger(__name__)
api_novel_chapter_url = "https://wuxia.click/api/chapters/"
home_url = "https://wuxia.click/"


class WuxiaClick(Crawler):
    base_url = ["https://wuxia.click/"]
    search_results_data = []

    def search_novel(self, query):

        soup = self.get_soup(home_url + "search/" + query)
        # json is inside <script id="__NEXT_DATA__" type="application/json"></script>

        script = soup.find("script", {"id": "__NEXT_DATA__"})
        data = json.loads(script.contents[0])

        data = data["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"][
            "data"
        ]["results"]

        results = []
        for novel in data:
            results.append(
                {
                    "title": novel["name"],
                    "url": home_url + "novel/" + novel["slug"],
                    "info": "Latest: %s" % novel["chapters"],
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        novel_data = json.loads(script.contents[0])
        novel_data = novel_data["props"]["pageProps"]["dehydratedState"]["queries"][0][
            "state"
        ]["data"]

        possible_title = novel_data["name"]
        assert possible_title, "No novel title"
        self.novel_title = possible_title
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = novel_data["author"]["name"]
        logger.info('%s', self.novel_author)

        self.novel_cover = novel_data["image"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_synopsis = novel_data["description"]
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        self.novel_tags = [x["name"] for x in novel_data["categories"]] + [
            x["name"] for x in novel_data["tags"]
        ]
        logger.info("Novel tags: %s", self.novel_tags)

        slug = novel_data["slug"]
        chapter_data = self.get_response(api_novel_chapter_url + slug + "/?format=json").json()
        for chapter in chapter_data:
            chap_id = chapter["index"]
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": chapter["title"],
                    "url": home_url + "chapter/" + chapter["novSlugChapSlug"],
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        script = soup.find("script", {"id": "__NEXT_DATA__"})
        chapter_data = json.loads(script.contents[0])
        contents = chapter_data["props"]["pageProps"]["dehydratedState"]["queries"][0]["state"]["data"]["text"]

        contents = "<p>" + contents.replace("\n", "</p><p>") + "</p>"
        return contents
