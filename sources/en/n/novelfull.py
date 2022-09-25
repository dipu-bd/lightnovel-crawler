# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote
from lncrawl.core.crawler import Crawler
from lncrawl.models.search_result import SearchResult

logger = logging.getLogger(__name__)
search_url = "https://novelfull.com/search?keyword=%s"

RE_VOLUME = r"(?:book|vol|volume) (\d+)"


class NovelFullCrawler(Crawler):
    base_url = [
        "http://novelfull.com/",
        "https://novelfull.com/",
    ]

    def search_novel(self, query):
        soup = self.get_soup(f"{self.home_url}search?keyword={quote(query)}")
        results = []
        for div in soup.select("#list-page .archive .list-truyen > .row"):
            a = div.select_one(".truyen-title a")
            info = div.select_one(".text-info a .chapter-text")
            results.append(
                SearchResult(
                    title=a.text.strip(),
                    url=self.absolute_url(a["href"]),
                    info=info.text.strip() if info else "",
                )
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one(".info-holder .book img")
        self.novel_title = image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        authors = []
        for a in soup.select(".info-holder .info a"):
            if a["href"].startswith("/author/"):
                authors.append(a.text.strip())
        self.novel_author = ", ".join(authors)
        logger.info("Novel author: %s", self.novel_author)

        pagination_link = soup.select_one("#list-chapter .pagination .last a")
        page_count = int(str(pagination_link["data-page"])) if pagination_link else 0
        logger.info("Chapter list pages: %d" % page_count)

        logger.info("Getting chapters...")
        futures = [
            self.executor.submit(self.download_chapter_list, i + 1)
            for i in range(page_count + 1)
        ]

        self.chapters = []
        possible_volumes = set([])
        for f in futures:
            for chapter in f.result():
                chapter_id = len(self.chapters) + 1
                volume_id = (chapter_id - 1) // 100 + 1
                possible_volumes.add(volume_id)
                self.chapters.append(
                    {
                        "id": chapter_id,
                        "volume": volume_id,
                        "title": chapter["title"],
                        "url": chapter["url"],
                    }
                )

        self.volumes = [{"id": x} for x in possible_volumes]

    def download_chapter_list(self, page):
        url = self.novel_url.split("?")[0].strip("/")
        url += "?page=%d&per-page=50" % page
        soup = self.get_soup(url)
        chapters = []
        for a in soup.select("ul.list-chapter li a"):
            title = a["title"].strip()
            chapters.append(
                {
                    "title": title,
                    "url": self.absolute_url(a["href"]),
                }
            )
        return chapters

    def initialize(self) -> None:
        self.cleaner.blacklist_patterns.update(["Read more chapter on NovelFull"])
        self.cleaner.bad_css.update(
            ['div[align="left"]', 'img[src*="proxy?container=focus"]']
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#chapter-content")
        return self.cleaner.extract_contents(contents)
