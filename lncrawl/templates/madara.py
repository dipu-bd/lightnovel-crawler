from typing import Iterable, Optional
from urllib.parse import urlencode

from ..context import ctx
from ..core import BrowserTemplate, Novel, PageSoup, Volume
from ..exceptions import LNException


class MadaraTemplate(BrowserTemplate):
    is_template = True

    search_item_selector = ".post-title h3 a"

    novel_title_selector = ".post-title h1"
    novel_cover_selector = ".summary_image a img"
    novel_author_selector = '.author-content a[href*="manga-author"]'
    novel_tags_selector = '.genres-content a[rel="tag"]'
    novel_synopsis_selector = ".description-summary a"

    chapter_list_selector = "ul.main .wp-manga-chapter a"
    chapter_body_selector = "div.reading-content"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
        self.cleaner.bad_css.update(['a[href="javascript:void(0)"]'])

    def build_search_url(self, query: str):
        params = dict(
            s=query,
            post_type="wp-manga",
            op="",
            author="",
            artist="",
            release="",
            adult="",
        )
        return f"{self.scraper.origin}?{urlencode(params)}"

    def parse_search_item_info(self, soup: PageSoup) -> str:
        latest = soup.select_one(".latest-chap .chapter a")
        votes = soup.select_one(".rating .total_votes")
        return "%s | Rating: %s" % (latest.text, votes.text)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_title_selector)
        tag.decompose("span")
        novel.title = tag.text

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        try:
            clean_novel_url = novel.url.split("?")[0].strip("/")
            response = self.scraper.submit_form(f"{clean_novel_url}/ajax/chapters/")
            soup = self.scraper.make_soup(response)
            chapters = soup.select(self.chapter_list_selector)
            return reversed(list(chapters))
        except Exception:
            ctx.logger.debug("Failed to fetch chapters using ajax", exc_info=True)

        nl_id = soup.select_one("#manga-chapters-holder[data-id]")
        if not nl_id:
            raise LNException("No chapter id tag found for alternate method")

        try:
            response = self.scraper.submit_form(
                f"{self.scraper.origin}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": nl_id["data-id"],
                },
            )
            soup = self.scraper.make_soup(response)
            chapters = soup.select(self.chapter_list_selector)
            return reversed(list(chapters))
        except Exception as e:
            raise LNException("Failed to fetch chapters using alternate method") from e
