# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Tuple
from urllib.parse import quote_plus, urlencode

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)


class NoveLightCrawler(BrowserTemplate):
    base_url = "https://novelight.net/"

    search_item_list_selector = ".manga-grid-list a.item"

    novel_title_selector = "header.header-manga h1"
    novel_cover_selector = "div.second-information div.poster img"
    novel_synopsis_selector = "div#information section.text-info"
    novel_tags_selector = "div#information section.tags a[href^='/catalog/?tags=']"
    novel_author_selector = ".mini-info a[href^='/character/'] div.info"

    chapter_list_selector = "select#select-pagination-chapter > option"
    chapter_title_selector = ".title"
    chapter_body_selector = ".chapter-text"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["div.advertisment"])

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}catalog/?search={quote_plus(query.lower())}"

    def _extract_book_tokens(self, soup: PageSoup) -> Tuple[str, str]:
        page_scripts = soup.select("body > script:not([src])")
        scripts_joined = "\n".join(str(s) for s in page_scripts)

        book_id_match = re.search(r'.*const BOOK_ID = "(\d+)".*', scripts_joined)
        if not book_id_match:
            raise LNException("Could not extract book_id from novel page")
        book_id = book_id_match.group(1)

        csrf_match = re.search(r'.*window.CSRF_TOKEN = "(\w+)".*', scripts_joined)
        if not csrf_match:
            raise LNException("Could not extract CSRF token from novel page")
        csrf = csrf_match.group(1)

        return book_id, csrf

    def parse_chapter_tags(self, soup: PageSoup, novel: Novel) -> Iterable[PageSoup]:
        book_id, csrf = self._extract_book_tokens(soup)
        novel.book_id = book_id
        novel.csrf = csrf

        encountered_paid_chapter = False
        chapters_lists = soup.select(self.chapter_list_selector)
        for page in self.taskman.progress_bar(
            reversed(chapters_lists),
            desc="Chapters",
            unit="page",
        ):
            params = {
                "csrfmiddlewaretoken": csrf,
                "book_id": book_id,
                "page": page["value"],
            }
            headers = {
                "Accept": "*/*",
                "Referer": novel.url,
                "x-requested-with": "XMLHttpRequest",
            }
            query = urlencode(params, True)
            url = f"{self.scraper.origin}book/ajax/chapter-pagination?{query}"
            data = self.scraper.get_json(url, headers)

            chapters_soup = self.scraper.make_soup(data["html"])
            for a in reversed(chapters_soup.select("a[href^='/book/chapter/']")):
                if a.select_one(".chapter-info .cost"):
                    encountered_paid_chapter = True
                yield a

        if encountered_paid_chapter:
            logger.warning("Paid chapters are not supported and will be skipped.")

    def download_chapter(self, chapter: Chapter) -> None:
        headers = {
            "Accept": "*/*",
            "Referer": chapter.url,
            "x-requested-with": "XMLHttpRequest",
        }
        url = chapter.url.replace("chapter", "ajax/read-chapter")
        data = self.scraper.get_json(url, headers=headers)
        soup = data["content"]
        contents = soup.select_one(".chapter-text")
        self.cleaner.clean_contents(contents)
        chapter.body = contents.inner_html
