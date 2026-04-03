# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)


class NovelGate(SoupTemplate):
    can_search = True
    base_url = [
        "https://novelgate.net/",
        "https://home.novel-gate.com/",
    ]

    chapter_body_selector = "#chapter-body"

    def search(self, query: str):
        query = query.lower().replace(" ", "%20")
        soup = self.scraper.get_soup(f"{self.scraper.origin}search/{query}")
        for tab in soup.select(".film-item"):
            a = tab.select_one("a")
            if not a:
                continue
            latest = tab.select_one("label.current-status span.process").text
            yield SearchResult(
                title=a["title"],
                url=self.absolute_url(a["href"]),
                info=latest,
            )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        possible_title = soup.select_one(".name")
        novel.title = possible_title.text

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        novel.author = ", ".join([a.text for a in soup.select('a[href*="/author/"]')])

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        img = soup.select_one(".book-cover")
        if img and img.get("data-original"):
            novel.cover_url = self.absolute_url(img["data-original"])

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        for div in soup.select(".block-film #list-chapters .book"):
            vol_title = div.select_one(".title a").text
            if not vol_title:
                continue
            volume = novel.add_volume(title=vol_title)
            for a in div.select("ul.list-chapters li.col-sm-5 a"):
                novel.add_chapter(
                    title=a.text,
                    volume=volume.id,
                    url=self.absolute_url(a["href"]),
                )

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.body = str(soup)

    def format_text(self, text):
        """formats the text and remove bad characters"""
        text = re.sub(r"\u00ad", "", text, flags=re.UNICODE)
        text = re.sub(r"\u201e[, ]*", "&ldquo;", text, flags=re.UNICODE)
        text = re.sub(r"\u201d[, ]*", "&rdquo;", text, flags=re.UNICODE)
        text = re.sub(r"[ ]*,[ ]+", ", ", text, flags=re.UNICODE)
        return text.strip()
