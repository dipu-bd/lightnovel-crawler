# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter

logger = logging.getLogger(__name__)
search_url = "https://ixdzs8.tw/bsearch?q=%s"


class IxdzsCrawler(Crawler):
    base_url = ["https://ixdzs8.tw/", "https://ixdzs8.com/",  # new
                "https://tw.m.ixdzs.com/", "https://www.aixdzs.com"]  # legacy / redirect domains

    def initialize(self) -> None:
        self.cleaner.bad_css.add("p.abg")  # advertisement

    @staticmethod
    def rectify_url(url: str) -> str:
        """
        This manually 'fixes' URLs and prepares them for usage later on in string templating.
        """
        url = url[:-1] if not url.endswith("/") else url
        if "https://tw.m.ixdzs.com" in url:
            return url.replace("https://tw.m.ixdzs.com", "https://ixdzs8.tw")
        if "https://www.aixdzs.com" in url:
            return url.replace("https://www.aixdzs.com", "https://ixdzs8.com")
        return url

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)
        results = []

        for data in soup.select(
            "main > div.panel > ul.u-list > li.burl"
        ):
            title = data.select_one("h3 a").get_text().strip()
            url = self.absolute_url(data.select_one("h3 a")["href"])
            results.append(
                {
                    "title": title,
                    "url": url,
                }
            )
        return results

    def read_novel_info(self):
        """Get novel title, author, cover etc"""
        self.novel_url = self.rectify_url(self.novel_url)
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)
        content = soup.select_one("div.novel")
        metadata = content.select_one("div.n-text")

        possible_title = metadata.select_one("h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.get_text()
        logger.info(f"Novel title: {self.novel_title}")

        self.novel_author = metadata.select_one(
            "a.bauthor"
        ).get_text()
        logger.info(f"Novel Author: {self.novel_author}")

        possible_novel_cover = content.select_one("div.n-img > img")
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["src"])
        logger.info(f"Novel Cover: {self.novel_cover}")

        possible_synopsis = soup.select_one("p#intro")
        if possible_synopsis:
            self.novel_synopsis = possible_synopsis.get_text()

        logger.info("Getting chapters...")

        last_chap_a = soup.select_one("ul.u-chapter > li:nth-child(1) > a")
        last_chap_url = self.absolute_url(last_chap_a["href"])
        last_chap_id = int(last_chap_url.split("/")[-1][1:].replace(".html", "").strip())
        logger.info(f"URL: {last_chap_url}, {last_chap_id}")

        for chap_id in range(1, last_chap_id + 1):
            if len(self.chapters) % 100 == 0:
                vol_id = chap_id // 100 + 1
                vol_title = f"Volume {vol_id}"
                self.volumes.append(Volume(vol_id, vol_title))
            self.chapters.append(Chapter(
                id=chap_id,
                title=f"Chapter {chap_id}",
                url=f"{self.novel_url}/p{chap_id}.html",
            ))

    def download_chapter_body(self, chapter):

        logger.info(f"Downloading {chapter['url']}")
        soup = self.get_soup(chapter["url"])

        possible_chapter_title = soup.select_one("article.page-content > h3")
        if possible_chapter_title:
            chapter.title = possible_chapter_title.get_text().strip()

        content = soup.select("article.page-content section p")
        content = self.cleaner.clean_contents(content)
        content = "\n".join(str(p) for p in content)

        return content
