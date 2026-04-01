import logging

from lncrawl.core import BrowserTemplate, Chapter, PageSoup

logger = logging.getLogger(__name__)


class ReLibraryCrawler(BrowserTemplate):
    base_url = [
        "https://re-library.com/",
    ]

    novel_title_selector = ".entry-title"
    novel_cover_selector = ".entry-content table img"
    novel_author_selector = ".entry-content a[href*='/nauthor/']"
    chapter_list_selector = ".page_item > a"
    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        self.taskman.init_executor(1)
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

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        if "translations" not in chapter.url:
            soup = self.scraper.get_soup(chapter.url)
            page_el = soup.select_one(".entry-content > p[style*='center'] a")
            post_url = self.absolute_url(page_el["href"])
            if "page_id" in post_url:
                chapter.url = post_url
            else:
                novel_url = f"https://re-library.com/translations/{post_url.split('/')[4:5][0]}"
                response = self.scraper.get_soup(novel_url)
                chapters = response.select(".page_item > a")
                chapter.url = chapters[chapter.id - 1]["href"]
        return super().parse_chapter_body(soup, chapter)
