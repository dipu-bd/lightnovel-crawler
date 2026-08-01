from typing import Iterable, Optional
from urllib.parse import urlencode

from ..core import Novel, PageSoup, SoupTemplate, Volume


class MangaStreamTemplate(SoupTemplate):
    is_template = True

    search_item_list_selector = ".listupd > article, .listupd .bsx"
    search_item_url_selector = "a.tip, a[href]"
    search_item_title_selector = "h2, span.ntitle, .tt, a.tip"
    search_item_info_selector = "span.nchapter"

    novel_title_selector = "h1.entry-title"
    novel_cover_selector = ".thumbook img, meta[property='og:image'],.sertothumb img"
    novel_author_selector = ".spe a[href*='/writer/']"
    novel_tags_selector = ".bottom.tags a[href*='/tag/']"
    novel_synopsis_selector = ".entry-content"

    chapter_title_selector = ".epl-title"
    chapter_body_selector = "#readernovel, #readerarea, .entry-content"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}?{urlencode({'s': query})}"

    def parse_search_item_title(self, soup: PageSoup) -> str:
        for tag in soup.select(self.search_item_title_selector):
            title = tag.text.strip()
            if title:
                return title
        link = soup.select_one("a[title]")
        return str(link.get("title") or "").strip() if link else ""

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        first_li = tag.select_one(".eplister li")
        li_class = first_li.get_attr("class", "") if first_li else ""
        data_num = first_li.get_attr("data-num", "0") if first_li else "0"
        chapters = tag.select(".eplister li a")
        if data_num == "1" or "tseplsfrst" not in str(li_class):
            return reversed(list(chapters))
        else:
            return chapters
