# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag, NavigableString
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class KiteNovel(Crawler):
    base_url = "https://www.kitenovel.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("span.title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.col-md-4.col-sm-4 > img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one("div.col-md-8.col-sm-8.pt-2 > p:nth-child(2)")
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        # open chapter list page
        chapter_list_link = soup.select_one("a.btn-primary")
        assert isinstance(chapter_list_link, Tag)
        chapter_list_link = self.absolute_url(chapter_list_link["href"])

        logger.info("Visiting %s", chapter_list_link)
        soup = self.get_soup(chapter_list_link)

        for a in soup.select('a[href*="/read/"]'):
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
        contents = soup.select_one("#content")

        # NOTE: Some chapters will have bad formatting e.g no paragraphs, it's the chapters on the site not the crawler.
        for br in soup.findAll("br"):
            next_s = br.nextSibling
            if not (next_s and isinstance(next_s, NavigableString)):
                continue
            next2_s = next_s.nextSibling
            if next2_s and isinstance(next2_s, Tag) and next2_s.name == "br":
                break

        return self.cleaner.extract_contents(contents)
