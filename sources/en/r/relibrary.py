import logging
from typing import Generator

from bs4 import BeautifulSoup, Tag
from lncrawl.models import Chapter
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate

logger = logging.getLogger(__name__)


class ReLibraryCrawler(ChapterOnlyBrowserTemplate):
    base_url = [
        "https://re-library.com/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)
        self.cleaner.bad_css.update(
            [
                "tr",
                ".nextPageLink",
                ".prevPageLink",
                ".su-button",
                "a[href*='re-library.com']",
            ]
        )
        self.cleaner.bad_tag_text_pairs.update(
            {
                "h2": "References",
            }
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-title")
        return tag.text.strip()

    def parse_cover(self, soup: BeautifulSoup) -> str:
        tag = soup.select_one(".entry-content table img")
        src = tag.get("data-src") or tag.get("src")
        return self.absolute_url(src)

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for a in soup.select_one(".entry-content").select("a[href*='/nauthor/']"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        yield from soup.select(".page_item > a")

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        return Chapter(
            id=id,
            title=tag.text.strip(),
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return soup.select_one(".entry-content")

    def parse_chapter_body(self, chapter: Chapter, text: str) -> str:
        if "translations" not in chapter.url:
            soup = self.get_soup(chapter.url)
            page_el = soup.select_one(".entry-content > p[style*='center'] a")
            post_url = self.absolute_url(page_el["href"])
            if "page_id" in post_url:
                chapter.url = post_url
            else:
                novel_url = (
                    f"https://re-library.com/translations/{post_url.split('/')[4:5][0]}"
                )
                response = self.get_soup(novel_url)
                chapters = response.select(".page_item > a")
                chapter.url = chapters[chapter.id - 1]["href"]
        return super().parse_chapter_body(chapter, text)
