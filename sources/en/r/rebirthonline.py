# -*- coding: utf-8 -*-
import logging

from bs4 import BeautifulSoup

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

book_url = "https://www.rebirth.online/novel/%s"


class RebirthOnlineCrawler(Crawler):
    base_url = "https://www.rebirth.online/"

    def read_novel_info(self):
        self.novel_id = self.novel_url.split("rebirth.online/novel/")[1].split("/")[0]
        logger.info("Novel Id: %s", self.novel_id)

        self.novel_url = book_url % self.novel_id
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h2.entry-title a")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        translator = soup.find("h3", {"class": "section-title"}).findNext("p").text
        author = (
            soup.find("h3", {"class": "section-title"}).findNext("p").findNext("p").text
        )
        self.novel_author = "Author : %s, Translator: %s" % (author, translator)
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = None
        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select(".table_of_content ul li a"):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip(),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if len(soup.findAll("br")) > 10:
            contents = soup.find("br").parent
        else:
            remove = [
                "http://www.rebirth.online",
                "support Content Creators",
                "content-copying bots",
                "Firefox Reader's Mode",
                "content-stealing websites",
                "rebirthonlineworld@gmail.com",
                "PayPal or Patreon",
                "available for Patreons",
                "Join us on Discord",
                "enjoy this novel",
            ]
            contents = soup.find("div", {"class": "obstruction"}).select("p")
            for content in contents:
                for item in remove:
                    if item in content.text:
                        content.extract()
            tmp = ""
            for content in contents:
                tmp = tmp + "<p>" + content.text + "</p>"
                contents = BeautifulSoup(tmp, "lxml")

        return str(contents)
