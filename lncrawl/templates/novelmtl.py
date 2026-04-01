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

    pagination_selector = "#chapters .pagination a[href]"
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
        yield from soup.select(self.chapter_list_selector)

        paginations = soup.select(self.pagination_selector)
        if not paginations:
            return

        last_page_url = self.absolute_url(paginations[-1]["href"])
        common_page_url = last_page_url.split("?")[0]
        params = parse_qs(urlparse(last_page_url).query)
        page_count = int(params["page"][0])

        futures: List[Future[PageSoup]] = []
        for p in range(1, page_count + 1):
            params["page"] = [str(p)]
            url = f"{common_page_url}?{urlencode(params, doseq=True)}"
            task = self.taskman.submit_task(self.scraper.get_soup, url)
            futures.append(task)

        for page in self.taskman.resolve_as_generator(
            futures,
            desc="TOC",
            unit="page",
        ):
            if page:
                yield from page.select(self.chapter_list_selector)
