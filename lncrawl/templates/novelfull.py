import re
from typing import Iterable, Optional
from urllib.parse import urlencode

from ..core import BrowserTemplate, Chapter, Novel, PageSoup, Volume
from ..exceptions import LNException


class NovelFullTemplate(BrowserTemplate):
    is_template = True

    search_item_list_selector = "#list-page .row h3[class*='title'] > a"
    search_item_title_selector = "h3.title"
    search_item_info_selector = "span.chapter"

    novel_title_selector = "h3.title"
    novel_cover_selector = ".book img"
    novel_author_selector = ".info a[href*='/a/'], .info a[href*='/au/'], .info a[href*='author']"
    novel_tags_selector = ".info a[href*='/au/']"
    novel_synopsis_selector = ".desc-text"

    chapter_list_selector = "ul.list-chapter > li > a[href], select > option[value]"
    chapter_body_selector = "#chr-content, #chapter-content"

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}search?{urlencode({'keyword': query})}"

    def parse_search_item_title(self, soup: PageSoup) -> str:
        return soup.get_attr("title") or soup.text

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        novel.tags = []
        info_section = soup.select_one(".info, .info-meta")
        for li in info_section.select("li"):
            header = li.select_one("h3")
            if not header or ("Genre" not in header.text and "Tag" not in header.text):
                continue
            for a in li.select("a"):
                if a and a.text.strip():
                    novel.tags.append(a.text.strip())

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        nl_id = soup.select_one("#rating[data-novel-id]")["data-novel-id"]
        if not nl_id:
            raise LNException("No novel_id found")

        script = soup.find("script", string=re.compile(r"ajaxChapterOptionUrl\s+="))
        if script:
            url = f"{self.scraper.origin}ajax-chapter-option?novelId={nl_id}"
        else:
            url = f"{self.scraper.origin}ajax/chapter-archive?novelId={nl_id}"

        soup = self.scraper.get_soup(url)
        return soup.select("ul.list-chapter > li > a[href], select > option[value]")

    def parse_chapter_url(self, soup: PageSoup, chapter: Chapter) -> None:
        chapter.url = self.absolute_url(soup["href"] or soup["value"])

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        contents = soup.select_one("#chr-content, #chapter-content")
        contents.decompose("div")
        chapter.body = contents.inner_html
