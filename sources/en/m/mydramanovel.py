# -*- coding: utf-8 -*-

import logging
import requests
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class MyDramaNovel(Crawler):
    base_url = ["https://mydramanovel.com/"]
    has_manga = False
    has_mtl = True

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_synopsis = self.cleaner.extract_contents(
            soup.find("div", {"class": "tagdiv-type"})
        )

        self.novel_cover = self.absolute_url(
            soup.find("span", {"class": "entry-thumb"}).get("data-img-url")
        )

        self.novel_title = soup.find("h1", {"class": "tdb-title-text"}).text

        # the synopsis may start like this :
        # "<p>Original Title: 春花厌</p><p>Author: Hei Yan</p><p>Raw Link : Chun Hua Yan</p><p>Mal..."
        # try to extract the author from the synopsis safely
        try:
            self.novel_author = (
                self.novel_synopsis.split("<p>Author:")[1].split("</p>")[0].strip()
            )
        except:
            self.novel_author = None

        self.volumes.append(
            {
                "id": 0,
                "title": self.novel_title,
            }
        )

        # the first five chapters are the first five a.td-image-wrap
        # The rest are normal divs
        preview_chapters = soup.select("a.td-image-wrap")[0:5]
        for preview_chapter in preview_chapters:
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "volume": 0,
                    "url": self.absolute_url(preview_chapter.get("href")),
                    "title": preview_chapter.get("title"),
                }
            )

        for chapter in soup.select(
            "div.tdb_module_loop.td_module_wrap.td-animation-stack.td-cpt-post"
        ):
            chapter_title = chapter.select_one("h3.entry-title a")
            if not chapter_title:
                continue
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "volume": 0,
                    "url": self.absolute_url(chapter_title.get("href")),
                    "title": chapter_title.text,
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        content = soup.find("div", {"class": "tagdiv-type"})
        return self.cleaner.extract_contents(content)
