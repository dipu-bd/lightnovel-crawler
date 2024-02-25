# -*- coding: utf-8 -*-
import logging

from bs4 import Tag

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, Volume
from sources.zh.uukanshu_sj import UukanshuOnlineSJ

logger = logging.getLogger(__name__)

novel_search_url = "%ssearch.aspx?k=%s"


class UukanshuOnline(Crawler):
    # www is simplified cn, tw is traditional cn but both use same site structure
    base_url = ["https://www.uukanshu.net/", "https://tw.uukanshu.net/"]

    encoding = "gbk"

    def initialize(self):
        # the default lxml parser cannot handle the huge gbk encoded sites (fails after 4.3k chapters)
        self.init_parser("html.parser")

    def read_novel_info(self) -> None:
        # the encoding for tw is utf-8, for www. is gbk -> otherwise output is messed up with wrong symbols.
        if "tw." in self.novel_url:
            self.encoding = "utf-8"

        soup = self.get_soup(self.novel_url, encoding=self.encoding)
        info = soup.select_one("dl.jieshao")
        assert info  # if this fails, HTML structure has fundamentally changed -> needs update
        meta = info.select_one("dd.jieshao_content")

        img = info.select_one("dt.jieshao-img img")
        if img:
            self.novel_cover = self.absolute_url(img["src"])

        self.novel_title = meta.select_one("h1 > a").text
        self.novel_author = meta.select_one("h2 > a").text
        synopsis = meta.select_one("h3")
        # in some cases the synopsis is only h3 without self-promo, but otherwise actual content is in paragraph
        if synopsis:
            self.novel_synopsis = synopsis.text
            if synopsis.select_one("p"):
                self.novel_synopsis = synopsis.select_one("p").text

        chapters = soup.select_one("ul#chapterList")
        for chapter in list(chapters.children)[::-1]:  # reverse order as it's newest to oldest
            # convince typehint that we're looking at Tags & also make sure we skip random text within the ul if any
            if not isinstance(chapter, Tag):
                continue
            # find chapters
            if chapter.has_attr("class") and "volume" in chapter["class"]:
                self.volumes.append(
                    Volume(
                        id=len(self.volumes) + 1,
                        title=chapter.text.strip(),
                    )
                )
                continue
            anchor = chapter.select_one("a")
            if not anchor:
                logger.warning("Found <li> in chapter list, not volume, without link: %s", chapter)
                continue
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    url=self.absolute_url(anchor["href"]),
                    title=anchor.text,
                    volume=len(self.volumes),
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url, encoding=self.encoding)
        content = soup.select_one("div#contentbox")
        # use same filters as already implemented on essentially same site
        return UukanshuOnlineSJ.format_text(self.cleaner.extract_contents(content))
