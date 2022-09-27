# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class IdqidianCrawler(Crawler):
    base_url = "https://www.idqidian.us/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find_all("span", {"typeof": "v:Breadcrumb"})[-1].text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = "https://www.idqidian.us/images/noavailable.jpg"
        logger.info("Novel cover: %s", self.novel_cover)

        author = soup.select("p")[3].text
        self.novel_author = author[20 : len(author) - 22]
        logger.info("Novel author: %s", self.novel_author)

        chapters = soup.find(
            "div",
            {
                "style": "-moz-border-radius: 5px 5px 5px 5px; border: 1px solid #333;"
                + " color: black; height: 400px; margin: 5px; overflow: auto; padding: 5px; width: 96%;"
            },
        ).findAll("a")
        chapters.reverse()

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        for a in soup.find_all("a"):
            a.extract()

        body_parts = soup.select("p")
        body_parts = "".join(
            [
                str(p.extract())
                for p in body_parts
                if p.text.strip()
                and "Advertisement" not in p.text
                and "JavaScript!" not in p.text
            ]
        )
        if body_parts == "":
            texts = [str.strip(x) for x in soup.strings if str.strip(x) != ""]
            unwanted_text = [str.strip(x.text) for x in soup.find_all()]
            my_texts = set(texts).difference(unwanted_text)
            body_parts = "".join(
                [
                    str(p)
                    for p in my_texts
                    if p.strip() and "Advertisement" not in p and "JavaScript!" not in p
                ]
            )

        return body_parts
