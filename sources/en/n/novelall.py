# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.novelall.com/search/?name=%s"


class NovelAllCrawler(Crawler):
    base_url = "https://www.novelall.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select(".cover-info p.title a")[:20]:
            url = self.absolute_url(a["href"])
            results.append(
                {
                    "url": url,
                    "title": a.text.strip(),
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url + "?waring=1")

        possible_title = soup.select_one(".manga-detail h1")
        assert isinstance(possible_title, Tag), "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".manga-detail img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        author = soup.find("div", {"class": "detail-info"}).find("a").text.split(",")
        if len(author) == 2:
            self.novel_author = author[0] + " (" + author[1] + ")"
        else:
            self.novel_author = " ".join(author)
        logger.info("Novel author: %s", self.novel_author)

        chapters = soup.find("div", {"class": "manga-detailchapter"}).findAll(
            "a", title=True
        )
        chapters.reverse()
        for a in chapters:
            for span in a.findAll("span"):
                span.extract()

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x["title"] or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.find("div", {"class": "reading-box"})
        self.cleaner.clean_contents(contents)
        return str(contents)
