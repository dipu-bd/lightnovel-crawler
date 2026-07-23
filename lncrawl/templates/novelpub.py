import re
from typing import Iterable, Optional

from ..core import Chapter, Novel, PageSoup, SoupTemplate, Volume
from ..exceptions import LNException

digit_regex = re.compile(r"page[-,=](\d+)")


class NovelPubTemplate(SoupTemplate):
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
    request_rate_limit = 3

    def initialize(self) -> None:
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

    def get_search_page_soup(self, query: str) -> PageSoup:
        return self.scraper.get_soup(f"{self.scraper.origin}search")

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        soup = self.get_search_page_soup(query)
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

    def parse_search_item_info(self, soup: PageSoup) -> str:
        info_tags = soup.select(self.search_item_info_selector)
        return " | ".join([x.text.strip() for x in info_tags])

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_list_url = f"{novel.url.strip('/')}/chapters"
        tag = self.scraper.get_soup(chapter_list_url)

        # get the results from first page
        yield from tag.select(self.chapter_list_selector)

        # get the total number of pages
        page_count = 1
        for a in tag.select(self.chapter_list_pagination_selector):
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
        for page in self.taskman.resolve(futures, desc="TOC", unit="page"):
            if page is not None:
                yield from page.select(self.chapter_list_selector)

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.title = soup.get("title") or soup.text
