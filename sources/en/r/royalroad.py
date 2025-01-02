# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.royalroad.com/fictions/search?keyword=%s"


class RoyalRoadCrawler(Crawler):
    base_url = "https://www.royalroad.com/"

    def initialize(self):
        self.init_executor(1)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select("h2.fiction-title a")[:5]:
            url = self.absolute_url(a["href"])
            results.append(
                {
                    "url": url,
                    "title": a.text.strip(),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "font-white"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find("img", {"class": "thumbnail inline-block"})["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.find("a", {"class": "font-white"}).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = self.cleaner.extract_contents(
            soup.find("div", {"class": "hidden-content"})
        )
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for tag in soup.find_all("a", {"class": "fiction-tag"}):
            self.novel_tags.append(tag.text)
        logger.info("Novel tags: %s", self.novel_tags)

        chapter_rows = soup.find("tbody").findAll("tr")
        chapters = [row.find("a", href=True) for row in chapter_rows]

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one("h2")
        if possible_title and "Chapter" in possible_title.text:
            chapter["title"] = possible_title.text.strip()

        classnames = []
        for style in soup.select("style"):
            style = style.text.replace(" ", "").replace("\n", "")
            if style.endswith("{display:none;speak:never;}"):
                classnames.append(style[1:-27])

        for classname in classnames:
            for div in soup.find_all("p", {"class": classname}):
                div.decompose()

        contents = soup.select_one(".chapter-content")
        self.cleaner.clean_contents(contents)
        return str(contents)
