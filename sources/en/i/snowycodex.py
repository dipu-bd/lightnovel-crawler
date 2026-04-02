# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Novel, PageSoup, SoupTemplate

logger = logging.getLogger(__name__)


class SnowyCodexCrawler(SoupTemplate):
    base_url = "https://snowycodex.com/"

    novel_title_selector = ".entry-content h2"
    novel_cover_selector = ".entry-content img"
    novel_synopsis_selector = ".entry-content p"
    chapter_list_selector = ".entry-content a[href*='/chapter']"
    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            {
                ".wpulike",
                ".sharedaddy",
                ".wpulike-default",
                '[style="text-align:center;"]',
            }
        )
        self.cleaner.bad_tag_text_pairs.update(
            {
                "p": r"[\u4E00-\u9FFF]+",
            }
        )

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.find("strong", string="Author:")
        novel.author = tag.next_sibling.text
