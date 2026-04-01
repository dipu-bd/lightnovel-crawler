import re
from typing import Iterable, Optional

from ..core import BrowserTemplate, Chapter, Novel, PageSoup, Volume
from ..exceptions import LNException

digit_regex = re.compile(r"page[-,=](\d+)")


class NovelPubTemplate(BrowserTemplate):
    is_template = True

    search_item_list_selector = ".novel-list .novel-item a"
    search_item_title_selector = ".novel-title"
    search_item_info_selector = ".novel-stats"

    novel_title_selector = "article#novel .novel-title"
    novel_cover_selector = "article#novel figure.cover > img"
    novel_author_selector = "article#novel span[itemprop='author']"
    novel_tags_selector = "article#novel .categories a"
    novel_synopsis_selector = "article#novel .summary .content"

    chapter_list_pagination_selector = ".pagination-container li a[href]"
    chapter_list_selector = "ul.chapter-list li a"
    chapter_title_selector = ".chapter-title"
    chapter_body_selector = ".chapter-content"

    def initialize(self) -> None:
        self.taskman.init_executor(workers=3)
        self.cleaner.bad_tags.update(["div"])
        self.cleaner.bad_css.update(
            [
                ".adsbox",
                ".ad-container",
                "p > strong > strong",
                ".OUTBRAIN",
                "p[class]",
                ".ad",
                "p:nth-child(1) > strong",
                ".noveltopads",
                ".chadsticky",
            ]
        )

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.scraper.get_soup(f"{self.scraper.origin}search")
        token_tag = soup.select_one('#novelSearchForm input[name="__LNRequestVerifyToken"]')
        if not token_tag:
            raise LNException("No request verify token found")
        token = token_tag["value"]

        response = self.scraper.submit_form(
            f"{self.scraper.origin}lnsearchlive",
            data={
                "inputContent": query,
            },
            headers={
                "lnrequestverifytoken": token,
                "referer": f"{self.scraper.origin}search",
            },
        )

        result_view = response.json()["resultview"]
        soup = self.scraper.make_soup(result_view)
        return soup.select(self.search_item_list_selector)

    # def select_search_items_in_browser(self, query: str) -> Generator[PageSoup, None, None]:
    #     self.visit(f"{self.home_url}search")
    #     self.browser.wait("#inputContent")
    #     inp = self.browser.find("#inputContent")
    #     if not inp:
    #         return
    #     inp.send_keys(query)
    #     self.browser.wait("#novelListBase ul, #novelListBase center")
    #     base = self.browser.find("#novelListBase")
    #     if not base:
    #         return
    #     yield from base.as_tag().select(".novel-list .novel-item a")

    def parse_search_item_info(self, soup: PageSoup) -> str:
        info_tags = soup.select(self.search_item_info_selector)
        return " | ".join([x.text.strip() for x in info_tags])

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_list_url = f"{novel.url.strip('/')}/chapters"
        soup = self.scraper.get_soup(chapter_list_url)

        # get the results from first page
        yield from soup.select(self.chapter_list_selector)

        # get the total number of pages
        page_count = 1
        for a in soup.select(self.chapter_list_pagination_selector):
            match = digit_regex.search(str(a["href"]))
            v = int(match.group(1)) if match else 0
            page_count = max(page_count, v)

        # get the results from 2nd page to last page
        futures = [
            self.taskman.submit_task(
                self.scraper.get_soup,
                f"{chapter_list_url}/page-{p}",
            )
            for p in range(2, page_count + 1)
        ]
        for page in self.taskman.resolve_as_generator(futures, desc="TOC", unit="page"):
            if page is not None:
                yield from page.select(self.chapter_list_selector)

    # def select_chapter_tags_in_browser(self):
    #     next_link = f"{self.novel_url}chapters"
    #     while next_link:
    #         self.browser.visit(next_link)
    #         self.browser.wait("ul.chapter-list li")
    #         chapter_list = self.browser.find("ul.chapter-list")
    #         if not chapter_list:
    #             return
    #         yield from chapter_list.as_tag().select("li a")
    #         try:
    #             next = self.browser.find('.PagedList-skipToNext a[href][rel="next"]')
    #             if not next:
    #                 break
    #             next_link = str(next.get_attribute("href"))
    #         except Exception:
    #             break

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.title = soup.get("title") or soup.text
