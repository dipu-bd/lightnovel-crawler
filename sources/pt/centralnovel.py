# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/?s=%s"


class CentralNovelCrawler(Crawler):
    base_url = [
        "https://centralnovel.com/",
    ]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % (self.home_url, query))

        results = []
        for article in soup.select(".listupd > .bs"):
            a = article.select_one(".bsx a.tip")
            title = article.select_one(".bsx span.ntitle")
            info = article.select_one(".bsx span.nchapter")

            results.append(
                {
                    "title": title.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info.text.strip(),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        if possible_title:
            self.novel_title = possible_title.get_text()

        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".thumbook img.wp-post-image")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["data-src"])

        logger.info("Novel cover: %s", self.novel_cover)

        for span in soup.select(".spe span"):
            text = span.text.strip()
            if text.startswith("Author:"):
                authors = span.select("a")
                if len(authors) == 2:
                    self.novel_author = authors[0].text + " (" + authors[1].text + ")"
                elif len(authors) == 1:
                    self.novel_author = authors[0].text
                break

        logger.info("Novel author: %s", self.novel_author)

        volumes = reversed(soup.select(".ts-chl-collapsible"))

        for vol_id, volume in enumerate(volumes, 1):
            self.volumes.append({"id": vol_id, "title": volume.text})

            for a in reversed(volume.next_sibling.select(".eplister li > a")):
                chap_id = 1 + len(self.chapters)

                epl_num = a.select_one(".epl-num").text.strip()
                epl_title = a.select_one(".epl-title").text.strip()

                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": f"{epl_num}: {epl_title}",
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content")
        return self.cleaner.extract_contents(contents)
