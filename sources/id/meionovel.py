# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://meionovels.com/wp-admin/admin-ajax.php"


class MeionovelCrawler(Crawler):
    base_url = ["https://meionovel.id/", "https://meionovels.com/"]

    def initialize(self):
        self.home_url = "https://meionovels.com/"

    def search_novel(self, query):
        data = self.submit_form(
            search_url,
            {
                "action": "wp-manga-search-manga",
                "title": query,
            },
        ).json()

        results = []
        for novel in data["data"]:
            titleSoup = self.make_soup(novel["title"])
            results.append(
                {
                    "title": titleSoup.body.text.title(),
                    "url": self.absolute_url(novel["url"]),
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # Title
        possible_title = soup.select_one(".post-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # Cover
        self.novel_cover = self.absolute_url(
            soup.select_one(".summary_image img")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        # Author
        possible_authors = [a.text.strip() for a in soup.select(".author-content a")]
        self.novel_author = ", ".join(filter(None, possible_authors))
        logger.info("Novel author: %s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        # Synopsis
        possible_synopsis = soup.select_one(".summary__content")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel summary: %s", self.novel_synopsis)

        # Tags
        possible_tags = soup.select(".genres-content a")
        if possible_tags:
            self.novel_tags = [a.text.strip() for a in possible_tags]
        logger.info("Novel tags: %s", self.novel_tags)

        # Chapters
        response = self.submit_form(self.novel_url.strip("/") + "/ajax/chapters")
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
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

        contents = soup.select_one("div.text-left")

        for img in contents.findAll("img"):
            if img.has_attr("data-lazy-src"):
                src_url = img["data-lazy-src"]
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        if contents.h3:
            contents.h3.extract()

        for codeblock in contents.findAll("div", {"class": "code-block"}):
            codeblock.extract()

        return str(contents)
