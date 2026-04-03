# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)


class PureTL(SoupTemplate):
    base_url = ["https://puretl.com/"]

    chapter_body_selector = ".blog-item-content"

    def initialize(self) -> None:
        self.cleaner.bad_text_regex.update(
            [
                "Consider supporting Pure and whitelisting",
                "If you enjoy this novel, please consider turning off ad-block! thank you~",
                "Check out our weekly update schedule HERE",
            ],
        )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        title_tag = soup.select_one("meta[property='og:title']")
        novel.title = title_tag.get("content").replace(
            "— Pure Love Translations English Translated Novels", ""
        )

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        possible_image = soup.select_one("meta[property='og:image']")
        if possible_image and possible_image.get("content"):
            novel.cover_url = self.absolute_url(possible_image["content"])

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        novel_author = soup.find("h4", string=re.compile(r"^By:"))
        if novel_author:
            novel.author = novel_author.text.split(":")[1].strip()
        logger.info("Novel author: %s", novel.author)

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        match = re.search(rf"{self.scraper.origin}(.*?)(/|\?|$)", novel.url)
        if not match:
            return
        slug = match.group(1)

        chapter_div = soup.select_one("div.accordion-block")
        content = next(chapter_div.parents("section"))
        for a in content.select(f"a[href*='{slug}/']"):
            novel.add_chapter(
                url=self.absolute_url(a["href"]),
                title=a.text.strip(),
            )

    def select_chapter_body(self, chapter: Chapter) -> PageSoup:
        soup = self.scraper.get_soup(chapter.url)
        title_el = soup.select_one(".entry-title")
        if title_el:
            chapter.title = title_el.text
        body = soup.select_one(self.chapter_body_selector)
        nav = body.find("a", string=re.compile("Index"))
        if nav and nav.parent:
            nav.parent.decompose()
        return body
