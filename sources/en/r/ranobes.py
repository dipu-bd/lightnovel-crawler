# -*- coding: utf-8 -*-
import json
import logging
import re
from concurrent.futures import Future
from typing import List, Optional
from urllib.parse import quote_plus, urljoin

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, Volume
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)


digit_regex = re.compile(r"\/(\d+)-")


class RanobeLibCrawler(BrowserTemplate):
    base_url = [
        "https://ranobes.top/",
        "https://ranobes.net/",
    ]

    search_item_list_selector = ".short-cont .title a"

    novel_title_selector = "h1.title"
    novel_cover_selector = ".r-fullstory-poster .poster a img"
    novel_author_selector = '.tag_list a[href*="/authors/"]'
    chapter_list_selector = ".cat_line a"
    chapter_title_selector = ".cat_line a"

    def initialize(self) -> None:
        self.cleaner.bad_css.update([".free-support", 'div[id^="adfox_"]'])

    def build_search_url(self, query: str) -> str:
        return urljoin(self.scraper.origin, "/search/{}/".format(quote_plus(query)))

    # def parse_chapter_list_in_browser(self) -> Generator[Chapter, None, None]:
    #     self.browser._driver.implicitly_wait(1)
    #     self.browser.click('a[href^="/chapters/"][title="Go to table of contents"]')

    #     index = 0
    #     while True:
    #         self.browser.wait(".cat_line a")
    #         for tag in self.browser.find_all(".cat_line a"):
    #             index += 1
    #             yield Chapter(
    #                 id=index,
    #                 title=tag.get_attribute("title"),
    #                 url=self.absolute_url(tag.get_attribute("href")),
    #             )

    #         next_page = self.browser.find(".page_next a")
    #         if not next_page:
    #             break
    #         self.browser._driver.implicitly_wait(1)
    #         next_page.scroll_into_view()
    #         next_page.click()

    def parse_chapter_list(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> None:
        id_match = digit_regex.search(novel.url)
        if not id_match:
            raise LNException("Could not extract novel id from URL")

        novel.id = id_match.group(1)
        chapter_list_url = urljoin(self.scraper.origin, f"/chapters/{novel.id}/")
        soup = self.scraper.get_soup(chapter_list_url)

        data = self._extract_page_data(soup)
        pages_count = data["pages_count"]
        futures: List[Future[PageSoup]] = []
        for i in reversed(range(2, pages_count + 1)):
            chapter_page_url = chapter_list_url.strip("/") + ("/page/%d" % i)
            task = self.taskman.submit_task(self.scraper.get_soup, chapter_page_url)
            futures.append(task)

        page_soups = [soup] + [
            page
            for page in self.taskman.resolve_as_generator(
                futures,
                desc="Chapters",
                unit="page",
            )
            if page
        ]

        novel.chapters = []
        for page in page_soups:
            data = self._extract_page_data(page)
            for chapter in reversed(data["chapters"]):
                chapter_id = len(novel.chapters) + 1
                chapter = Chapter(
                    id=chapter_id,
                    title=chapter["title"],
                    url=self.absolute_url(chapter["link"]),
                )
                novel.chapters.append(chapter)

    def _extract_page_data(self, soup: PageSoup) -> dict:
        script = soup.find(
            lambda tag: (
                bool(tag) and tag.name == "script" and tag.text.startswith("window.__DATA__")
            )
        )

        content = script.text.strip()
        content = content.replace("window.__DATA__ = ", "")

        data = json.loads(content)
        return data
