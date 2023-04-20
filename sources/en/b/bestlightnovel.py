# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://bestlightnovel.com/getsearchstory"
novel_page_url = "https://bestlightnovel.com/novel_%s"
change_bad_words_off = "https://bestlightnovel.com/change_bad_words_off"


class BestLightNovel(Crawler):
    base_url = "https://bestlightnovel.com/"

    def search_novel(self, query):
        data = self.submit_form(search_url, {"searchword": query}).json()

        results = []
        for novel in data:
            titleSoup = self.make_soup(novel["name"])
            results.append(
                {
                    "title": titleSoup.body.text.title(),
                    "url": novel_page_url % novel["id_encode"],
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

        possible_image = soup.select_one(".info_image img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ', '.join([
            a.text.strip()
            for a in soup.select('.truyen_info_right a[href*="search_author"]')
        ])
        logger.info('%s', self.novel_author)

        synopsis = soup.select_one("#noidungm")
        if synopsis.select_one("p"):
            synopsis.select_one("p").extract()
        self.novel_synopsis = self.cleaner.extract_contents(synopsis)

        self.novel_tags = [
            a.text.strip()
            for a in soup.select('.truyen_info_right a[href*="novel_list?type=latest&category="]')
        ]

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

        self.get_response(change_bad_words_off)

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if "Chapter" in soup.select_one("h1").text:
            chapter["title"] = soup.select_one("h1").text

        contents = soup.select_one("#vung_doc")
        return self.cleaner.extract_contents(contents)
