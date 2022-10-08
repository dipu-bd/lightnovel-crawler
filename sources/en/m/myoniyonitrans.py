# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlparse

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
novel_page = "https://myoniyonitranslations.com/%s"


class MyOniyOniTranslation(Crawler):
    base_url = "https://myoniyonitranslations.com/"

    def read_novel_info(self):
        path_fragments = urlparse(self.novel_url).path.split("/")
        novel_hash = path_fragments[1]
        if novel_hash == "category":
            novel_hash = path_fragments[2]
        self.novel_url = novel_page % novel_hash

        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        if not soup.select_one("article.page.type-page"):
            a = soup.select_one("header.entry-header p span:nth-of-type(3) a")
            if not a:
                raise Exception(
                    "Fail to recognize url as a novel page: " + self.novel_url
                )
            self.novel_url = a["href"]
            return self.read_novel_info()

        possible_title = soup.select_one("header.entry-header h1.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_authors = []
        for p in soup.select(".x-container .x-column.x-1-2 p"):
            if re.match(r"author|trans|edit", p.text, re.I):
                possible_authors.append(p.text.strip())
        if len(possible_authors):
            self.novel_author = ", ".join(possible_authors)
        logger.info("Novel author: %s", self.novel_author)

        possible_image = soup.select_one(".x-container img.x-img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract volume-wise chapter entries
        accordian = soup.select(".x-container .x-accordion .x-accordion-group")
        if accordian:
            for div in accordian:
                a = div.select_one("a.x-accordion-toggle")
                vol_id = len(self.volumes) + 1
                self.volumes.append({"id": vol_id, "title": a.text.strip()})
                for chap in div.select(".x-accordion-body a"):
                    self.chapters.append(
                        {
                            "volume": vol_id,
                            "id": len(self.chapters) + 1,
                            "title": chap.text.strip(" []"),
                            "url": self.absolute_url(chap["href"]),
                        }
                    )
        else:
            self.volumes.append({"id": 1})
            for a in soup.select(".entry-content p a"):
                possible_url = self.absolute_url(a["href"].lower())
                if not possible_url.startswith(self.novel_url):
                    continue
                self.chapters.append(
                    {
                        "volume": 1,
                        "id": len(self.chapters) + 1,
                        "url": possible_url,
                        "title": a.text.strip(" []"),
                    }
                )

        logger.debug(
            "%d chapters & %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("article div.entry-content")
        assert contents, "No chapter contents"

        # clean all upto first <hr>
        for tag in contents.select("*"):
            if tag.name == "hr":
                break
            tag.extract()

        self.cleaner.bad_tags.add("div")
        self.cleaner.clean_contents(contents)
        return str(contents)
