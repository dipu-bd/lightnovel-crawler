# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novelonlinefull.com/getsearchstory"
novel_page_url = "https://novelonlinefull.com/novel/%s"


class NovelOnlineFullCrawler(Crawler):
    base_url = "https://novelonlinefull.com/"

    def search_novel(self, query):
        response = self.submit_form(search_url, {"searchword": query})
        data = response.json()

        results = []
        for novel in data:
            titleSoup = BeautifulSoup(novel["name"], "lxml")
            results.append(
                {
                    "title": titleSoup.body.text.title(),
                    "url": novel_page_url % novel["nameunsigned"],
                    "info": "Latest: %s" % novel["lastchapter"],
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # self.novel_title = soup.select_one('h1.entry-title').text.strip()
        possible_title = soup.select_one("div.entry-header h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        try:
            novel_data = self.submit_form(
                search_url, {"searchword": self.novel_title}
            ).json()
            self.novel_cover = novel_data[0]["image"]
            self.novel_author = novel_data[0]["author"]
        except Exception:
            logger.debug("Failed getting novel info.\n%s", Exception)

        for a in reversed(soup.select("#list_chapter .chapter-list a")):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if "Chapter" in soup.select_one("h1").text:
            chapter["title"] = soup.select_one("h1").text
        else:
            chapter["title"] = chapter["title"]

        self.cleaner.bad_text_regex = set(
            [
                r"^translat(ed by|or)",
                r"(volume|chapter) .?\d+",
            ]
        )

        contents = soup.select_one("#vung_doc")
        return self.cleaner.extract_contents(contents)
