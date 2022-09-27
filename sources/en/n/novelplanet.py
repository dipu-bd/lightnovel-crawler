# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novelplanet.com/NovelList?order=mostpopular&name=%s"


class NovelPlanetCrawler(Crawler):
    base_url = "https://novelplanet.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("section a.title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".post-previewInDetails img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for span in soup.find_all("span", {"class": "infoLabel"}):
            if span.text == "Author:":
                author = span.findNext("a").text
                author2 = span.findNext("a").findNext("a").text
        # check if author word is found in second <p>
        if (author2 != "Ongoing") or (author2 != "Completed"):
            self.novel_author = author + " (" + author2 + ")"
        else:
            self.novel_author = author
        logger.info("Novel author: %s", self.novel_author)

        chapters = soup.find_all("div", {"class": "rowChapter"})
        chapters.reverse()

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x.find("a")["href"]),
                    "title": x.find("a")["title"] or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one("h4")
        if possible_title and possible_title.text:
            chapter["title"] = possible_title.text.strip()
        else:
            chapter["title"] = str(chapter["title"]).replace("Read Novel ", "")

        contents = soup.select_one("#divReadContent")
        assert contents, "No chapter contents"

        for ads in contents.findAll(
            "div", {"style": "text-align: center; margin-bottom: 10px"}
        ):
            ads.extract()

        return str(contents)

        # return ''.join([
        #    str(p).strip()
        #    for p in content.select('p')
        #    if p.text.strip()
        # ])
