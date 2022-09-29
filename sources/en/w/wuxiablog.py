# -*- coding: utf-8 -*-
import logging

from bs4 import ResultSet, Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class WuxiaBlogCrawler(Crawler):
    base_url = ["https://www.wuxia.blog/"]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [".recently-nav", ".pager", ".fa", "span[itemprop='datePublished']"]
        )
        self.cleaner.bad_tags.update(["h4"])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        title_tag = soup.select_one("h4.panel-title")
        if not isinstance(title_tag, Tag):
            raise LNException("No title found")

        self.novel_title = title_tag.text.strip()

        image_tag = soup.select_one(".imageCover img")
        if isinstance(image_tag, Tag):
            self.novel_cover = self.absolute_url(image_tag["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        author_tag = soup.select(".panel-body a[href*='/author/']")
        if isinstance(author_tag, ResultSet):
            self.novel_author = ", ".join([a.text.strip() for a in author_tag])

        chapters = soup.select("#chapters a")

        more_tag = soup.select_one("#more")
        if isinstance(more_tag, Tag):
            nid = more_tag["data-nid"]
            more_soup = self.post_soup(
                self.absolute_url(f"/temphtml/_tempChapterList_all_{nid}.html")
            )
            more_chapters = more_soup.select("a")
            chapters.extend(more_chapters)

        for a in reversed(chapters):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".panel-body.article")
        self.cleaner.clean_contents(contents)

        return str(contents)
