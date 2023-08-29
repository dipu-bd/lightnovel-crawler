# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.templates.mangastream import MangaStreamTemplate

logger = logging.getLogger(__name__)
search_url = 'https://novelsemperor.com/series?title=%s&type=novels&status='


class NovelsEmperorCrawler(MangaStreamTemplate):
    base_url = ["https://novelsemperor.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Thank you for reading this story at novelsemperor.com",
                "immediately rushed \\(Campaign period:",
                "promotion, charge 100 and get 500 VIP coupons!",
            ]
        )

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select("div.xlg\\:grid-cols-8.grid.grid-cols-3 div#card-real"):
            a = tab.select_one("a")
            title = a["href"][32:].replace('-', ' ')
            img = tab.select_one("img")["data-src"]
            results.append(
                {
                    "title": title,
                    "url": self.absolute_url(a["href"]),
                    "img": img,
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h2.text-2xl")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        author = soup.select('p:nth-child(4) > span.capitalize')
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one("div.relative > img")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        for div in soup.select("div#chapters-list"):
            vol_title = div.select_one("a div div span").text
            vol_id = [int(x) for x in re.findall(r"\d+", vol_title)]
            vol_id = vol_id[0] if len(vol_id) else len(self.volumes) + 1
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": vol_title,
                }
            )

            for a in div.select("a"):
                ch_title = a.select_one("div div span").text
                ch_id = [int(x) for x in re.findall(r"\d+", ch_title)]
                ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": ch_id,
                        "volume": vol_id,
                        "title": ch_title,
                        "url": self.absolute_url(a["href"]),
                    }
                )

        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.mx-auto.max-w-3xl")

        return str(contents)
