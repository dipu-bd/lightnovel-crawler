# -*- coding: utf-8 -*-
import logging
from math import ceil
from urllib.parse import quote

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
chapter_post_url = "https://www.scribblehub.com/wp-admin/admin-ajax.php"


class ScribbleHubCrawler(Crawler):
    base_url = [
        "https://www.scribblehub.com/",
        "https://scribblehub.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".p-avatar-wrap",
                ".sp-head",
                ".spdiv",
                ".chp_stats_feature",
                ".modern-footnotes-footnote",
                ".modern-footnotes-footnote__note",
                ".wi_authornotes",
            ]
        )
        self.cleaner.whitelist_attributes.update(
            [
                "border",
                "class",
            ]
        )
        self.cleaner.whitelist_css_property.update(
            [
                "text-align",
            ]
        )

    def search_novel(self, query):
        url = f"{self.home_url}?s={quote(query)}&post_type=fictionposts"
        soup = self.get_soup(url)

        results = []
        for novel in soup.select("div.search_body"):
            a = novel.select_one(".search_title a")
            info = novel.select_one(".search_stats")
            if not isinstance(a, Tag):
                continue

            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info.text.strip() if isinstance(info, Tag) else "",
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.fic_title")
        assert isinstance(possible_title, Tag)
        self.novel_title = str(possible_title["title"]).strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.find("div", {"class": "fic_image"})
        if isinstance(possible_image, Tag):
            possible_image = possible_image.find("img")
            if isinstance(possible_image, Tag):
                self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.find("span", {"class": "auth_name_fic"})
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        chapter_count = soup.find("span", {"class": "cnt_toc"})
        chapter_count = (
            int(chapter_count.text) if isinstance(chapter_count, Tag) else -1
        )
        page_count = ceil(chapter_count / 15.0)
        logger.info("Chapter list pages: %d" % page_count)

        possible_mypostid = soup.select_one("input#mypostid")
        assert isinstance(possible_mypostid, Tag)
        mypostid = int(str(possible_mypostid["value"]))
        logger.info("#mypostid = %d", mypostid)

        response = self.submit_form(
            f"{self.home_url}wp-admin/admin-ajax.php",
            {
                "action": "wi_getreleases_pagination",
                "pagenum": -1,
                "mypostid": mypostid,
            },
        )

        soup = self.make_soup(response)
        for chapter in reversed(soup.select(".toc_ol a.toc_a")):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "url": self.absolute_url(str(chapter["href"])),
                    "title": chapter.text.strip(),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#chp_raw")
        self.cleaner.clean_contents(contents)
        body = str(contents)
        body += """<style type="text/css">
        table {
            margin: 0 auto;
            border: 2px solid;
            border-collapse: collapse;
        }
        table td {
            padding: 10px;
        }
        </style>
        """
        return body
