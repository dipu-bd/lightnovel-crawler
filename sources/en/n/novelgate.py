# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novelgate.net/search/%s"


class NovelGate(Crawler):
    base_url = "https://novelgate.net/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "%20")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".film-item"):
            a = tab.select_one("a")
            latest = tab.select_one("label.current-status span.process").text
            results.append(
                {
                    "title": a["title"],
                    "url": self.absolute_url(a["href"]),
                    "info": "%s" % (latest),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".name")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        author = soup.find_all(href=re.compile("author"))
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one(".book-cover")["data-original"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        for div in soup.select(".block-film #list-chapters .book"):
            vol_title = div.select_one(".title a").text
            vol_id = [int(x) for x in re.findall(r"\d+", vol_title)]
            vol_id = vol_id[0] if len(vol_id) else len(self.volumes) + 1
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": vol_title,
                }
            )

            for a in div.select("ul.list-chapters li.col-sm-5 a"):
                ch_title = a.text
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

        contents = soup.select_one("#chapter-body")

        return str(contents)

    def format_text(self, text):
        """formats the text and remove bad characters"""
        text = re.sub(r"\u00ad", "", text, flags=re.UNICODE)
        text = re.sub(r"\u201e[, ]*", "&ldquo;", text, flags=re.UNICODE)
        text = re.sub(r"\u201d[, ]*", "&rdquo;", text, flags=re.UNICODE)
        text = re.sub(r"[ ]*,[ ]+", ", ", text, flags=re.UNICODE)
        return text.strip()
