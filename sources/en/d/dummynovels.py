# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class DummyNovelsCrawler(Crawler):
    base_url = "https://dummynovels.com/"

    def search_novel(self, query: str):
        keywords = set(query.lower().split())
        soup = self.get_soup("%s/novels/" % self.home_url)

        novels = {}
        for a in soup.select(".elementor-post .elementor-post__title a"):
            novels[a.text.strip().lower()] = {
                "title": a.text.strip(),
                "url": self.absolute_url(a["href"]),
            }

        results = []
        for haystack, novel in novels.items():
            if any(x in keywords for x in haystack.split()):
                results.append(novel)

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".elementor-heading-title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".elementor-image img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        for div in soup.select(".elementor-text-editor"):
            if div.text.startswith("Author"):
                self.novel_author = div.text.split(":")[-1].strip()
                break
        logger.info("Novel author: %s", self.novel_author)

        possible_toc = None
        for tab in soup.select(".elementor-tab-desktop-title[aria-controls]"):
            if "Table of Contents" in str(tab.text):
                possible_toc = soup.select_one("#" + str(tab["aria-controls"]))
                break
        assert isinstance(possible_toc, Tag), "No table of contents"

        for tab in possible_toc.select(
            ".elementor-accordion-item .elementor-tab-title"
        ):
            possible_contents = possible_toc.select_one("#" + str(tab["aria-controls"]))
            if not isinstance(possible_contents, Tag):
                continue

            vol_id = 1 + len(self.volumes)
            vol_title = tab.select_one(".elementor-accordion-title")
            vol_title = vol_title.text if isinstance(vol_title, Tag) else None
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": vol_title,
                }
            )

            for a in possible_contents.select("a"):
                chap_id = len(self.chapters) + 1
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
        contents = soup.select_one(".elementor-widget-theme-post-content")
        return self.cleaner.extract_contents(contents)
