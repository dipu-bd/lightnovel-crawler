import time
from concurrent.futures import Future
from typing import Iterable, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

from ..core import BrowserTemplate, Novel, PageSoup, Volume
from ..exceptions import LNException


class NovelMTLTemplate(BrowserTemplate):
    is_template = True

    search_item_list_selector = "ul.novel-list .novel-item a"
    search_item_title_selector = ".novel-title"
    search_item_info_selector = ".novel-stats"

    novel_title_selector = ".novel-info .novel-title"
    novel_cover_selector = "#novel figure.cover img"
    novel_author_selector = '.novel-info .author span[itemprop="author"]'
    novel_tags_selector = ".categories a"
    novel_synopsis_selector = ".summary .content"

    chapter_list_pagination_selector = "#chapters .pagination li a"
    chapter_list_selector = "ul.chapter-list li a"
    chapter_title_selector = ".chapter-title"
    chapter_body_selector = ".chapter-content"

    def initialize(self) -> None:
        self.cur_time = int(1000 * time.time())
        self.taskman.init_executor(ratelimit=1.4)

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.scraper.get_soup(f"{self.scraper.origin}search.html")
        form = soup.select_one('.search-container form[method="post"]')
        if not form:
            raise LNException("No search form")
        action_url = self.absolute_url(form["action"])
        payload = {input["name"]: input["value"] for input in form.select("input")}
        payload["keyboard"] = query
        response = self.scraper.submit_form(action_url, payload)
        soup = self.scraper.make_soup(response)
        return soup.select(self.search_item_list_selector)

    def parse_search_item_info(self, soup: PageSoup) -> str:
        info_tags = soup.select(self.search_item_info_selector)
        return " | ".join([x.text.strip() for x in info_tags])

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        paginations = list(soup.select(self.chapter_list_pagination_selector))
        if not paginations:
            yield from soup.select(self.chapter_list_selector)
            return

        last_page = str(paginations[-1]["href"])
        last_page_qs = parse_qs(urlparse(last_page).query)
        max_page = int(last_page_qs["page"][0])
        wjm = last_page_qs["wjm"][0]

        futures: List[Future] = []
        for i in range(max_page + 1):
            payload = {
                "page": i,
                "wjm": wjm,
                "_": self.cur_time,
                "X-Requested-With": "XMLHttpRequest",
            }
            url = f"{self.scraper.origin}e/extend/fy.php?{urlencode(payload)}"
            f = self.taskman.submit_task(self.scraper.get_soup, url)
            futures.append(f)

        for page in self.taskman.resolve_as_generator(
            futures,
            desc="TOC",
            unit="page",
        ):
            if page is None:
                raise LNException("Failed to get page")
            yield from page.select(self.chapter_list_selector)
