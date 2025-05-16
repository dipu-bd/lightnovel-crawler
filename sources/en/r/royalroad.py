# -*- coding: utf-8 -*-
import re
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
        for a in soup.select("h2.fiction-title a[href]")[:5]:
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".fic-header h1").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_cover = soup.select_one(".fic-header img.thumbnail[src]")
        if possible_cover:
            self.novel_cover = self.absolute_url(possible_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [a.text.strip() for a in soup.select('.fic-header a[href^="/profile/"]')]
        )
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = self.cleaner.extract_contents(
            soup.select_one(".fiction-info .description .hidden-content")
        )
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        self.novel_tags = [
            a.text.strip()
            for a in soup.select('.fiction-info .tags a[href^="/fictions/search"]')
        ]
        logger.info("Novel tags: %s", self.novel_tags)

        for a in soup.select("#chapters .chapter-row td:first-child a[href]"):
            chap_id = len(self.chapters) + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one("h2")
        if possible_title and "Chapter" in possible_title.text:
            chapter["title"] = possible_title.text.strip()

        hidden_class = ""
        for style in soup.select("head > style"):
            clean_text = re.sub(r"[\n\s]+", "", style.text.strip(), re.MULTILINE)
            matches = re.findall(r"(.[\d\w]+)\{display:none;speak:never;\}", clean_text)
            if matches:
                hidden_class = ",".join(matches)
                break

        contents = soup.select_one(".chapter .chapter-content")
        if hidden_class:
            for p in contents.select(hidden_class):
                p.decompose()

        self.cleaner.clean_contents(contents)
        return str(contents)
