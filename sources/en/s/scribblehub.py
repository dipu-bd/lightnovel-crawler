# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import BrowserTemplate, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)

digit_regex = re.compile(r"\?toc=(\d+)#content1$")


class ScribbleHubCrawler(BrowserTemplate):
    base_url = "https://www.scribblehub.com/"
    has_manga = False
    has_mtl = False

    novel_url_selector = ".fictionposts-template-default"
    novel_title_selector = ".fic_title"
    novel_cover_selector = ".fic_image img"
    novel_author_selector = ".auth_name_fic"
    novel_tags_selector = "a.fic_genre"
    novel_synopsis_selector = ".wi_fic_desc"

    chapter_list_selector = ".toc_ol a.toc_a"
    chapter_body_selector = "#chp_raw"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".p-avatar-wrap",
                ".sp-head",
                ".spdiv",
                ".chp_stats_feature",
                ".modern-footnotes-footnote",
                ".modern-footnotes-footnote__note",
                ".wi_authornotes",
            ]
        )
        self.cleaner.whitelist_attributes.update(
            [
                "border",
                "class",
            ]
        )
        self.cleaner.whitelist_css_property.update(
            [
                "text-align",
            ]
        )

    # def visit_novel_page_in_browser(self) -> PageSoup:
    #     url_parts = self.novel_url.split("/")
    #     self.novel_url = f"{url_parts[0]}/{url_parts[2]}/{url_parts[3]}/{url_parts[4]}/"
    #     logger.debug(self.novel_url)
    #     self.visit(self.novel_url)
    #     self.browser.wait(".fictionposts-template-default")

    def parse_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        chapter_count = -1
        chapter_count_tag = soup.select_one("span.cnt_toc")
        if chapter_count_tag.text.isdigit():
            chapter_count = int(chapter_count_tag.text)
        novel.chapter_count = chapter_count

        mypostid_tag = soup.select_one("input#mypostid[value]")
        mypostid = int(str(mypostid_tag["value"]))
        novel.mypostid = mypostid

        response = self.scraper.submit_form(
            f"{self.scraper.origin}wp-admin/admin-ajax.php",
            {
                "action": "wi_getreleases_pagination",
                "pagenum": -1,
                "mypostid": mypostid,
            },
        )
        soup = self.scraper.make_soup(response)
        return reversed(soup.select(self.chapter_list_selector))

    # def parse_chapter_list_in_browser(
    #     self,
    # ) -> Generator[Union[Chapter, Volume], None, None]:
    #     _pages = max(
    #         [
    #             int(digit_regex.search(a["href"]).group(1))
    #             for a in self.browser.soup.select(".simple-pagination a")
    #             if digit_regex.search(a["href"]) is not None
    #         ]
    #     )
    #     if not _pages:
    #         _pages = 1
    #     tags = self.browser.soup.select(".main .toc li a")
    #     for i in range(2, _pages + 1):
    #         self.browser.visit(urljoin(self.novel_url, f"?toc={i}#content1"))
    #         self.browser.wait(".main")
    #         tags += self.browser.soup.select(".main .toc li a")

    #     for _id, _t in enumerate(reversed(tags)):
    #         yield Chapter(id=_id, url=self.absolute_url(_t.get("href")), title=_t.text.strip())
