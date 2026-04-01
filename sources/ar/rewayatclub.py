# -*- coding: utf-8 -*-
import logging
import math

import execjs  # type: ignore

from lncrawl.core import Chapter, LegacyCrawler, PageSoup

logger = logging.getLogger(__name__)

chapter_list_url = "https://api.rewayat.club/api/chapters/%s/?ordering=number&page=%d"
chapter_body_url = "https://rewayat.club/novel/%s/%d"


class RewayatClubCrawler(LegacyCrawler):
    base_url = "https://rewayat.club/"

    def initialize(self) -> None:
        self.cleaner.bad_tags.clear()
        self.cleaner.bad_css.clear()
        self.cleaner.bad_css.update([".code-block"])

    def read_novel_info(self):
        self.is_rtl = True

        soup = self.get_soup(self.novel_url)
        data = self.extract_nuxt_data(soup)

        novel_info = data["fetch"][0]["novel"]
        pagination = data["fetch"][0]["pagination"]
        per_page = len(data["fetch"][0]["chapters"])

        self.novel_title = novel_info["arabic"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = "https://api.rewayat.club" + novel_info["poster_url"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join([x["username"] for x in novel_info["contributors"]])
        logger.info("Novel author: %s", self.novel_author)

        novel_slug = novel_info["slug"]
        logger.info("Novel slug: %s", novel_slug)

        total_items = pagination["count"]
        total_pages = math.ceil(total_items / per_page)
        logger.info("Total pages: %d", total_pages)

        futures = []
        for page in range(total_pages):
            url = chapter_list_url % (novel_slug, page + 1)
            f = self.executor.submit(self.get_json, url)
            futures.append(f)

        for f in futures:
            data = f.result()
            for item in data["results"]:
                self.chapters.append(
                    Chapter(
                        id=len(self.chapters) + 1,
                        title=item["title"],
                        url=chapter_body_url % (novel_slug, item["number"]),
                    )
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        data = self.extract_nuxt_data(soup)

        contents = data["fetch"][0]["contentParts"]
        contents = [x["content"] for y in contents for x in y]

        html = "\n".join(contents)
        html = html.replace("<span>", "").replace("</span>", "")
        body = self.make_soup(html).find("body")
        return self.cleaner.extract_contents(body)

    def extract_nuxt_data(self, soup: PageSoup) -> dict:
        script = soup.find(name="script", string=lambda s: s.startswith("window.__NUXT__"))
        script_content = script.text.replace("window.__NUXT__=", "")[:-1]

        data = execjs.eval(script_content)
        assert isinstance(data, dict)

        return data
