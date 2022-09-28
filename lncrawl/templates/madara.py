from typing import List
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models import Chapter, SearchResult


class MadaraTemplate(Crawler):
    is_template = True

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
        self.cleaner.bad_css.update(['a[href="javascript:void(0)"]'])

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_search_page_soup(query)
        return [
            self.parse_search_item(tab)
            for tab in soup.select(".c-tabs-item__content")
            if isinstance(tab, Tag)
        ]

    def get_search_page_soup(self, query: str) -> BeautifulSoup:
        return self.get_soup(
            f"{self.home_url}?s={quote(query)}&post_type=wp-manga&op=&author=&artist=&release=&adult="
        )

    def parse_search_item(self, tab: Tag) -> SearchResult:
        a = tab.select_one(".post-title h3 a")
        latest = tab.select_one(".latest-chap .chapter a").text
        votes = tab.select_one(".rating .total_votes").text
        return SearchResult(
            title=a.text.strip(),
            url=self.absolute_url(a["href"]),
            info="%s | Rating: %s" % (latest, votes),
        )

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)
        self.parse_title(soup)
        self.parse_image(soup)
        self.parse_authors(soup)
        self.parse_chapter_list(self.get_chapter_list_soup(soup))

    def parse_title(self, soup: BeautifulSoup) -> None:
        tag = soup.select_one(".post-title h1")
        if not isinstance(tag, Tag):
            raise LNException("No title found")
        for span in tag.select("span"):
            span.extract()
        self.novel_title = tag.text.strip()

    def parse_image(self, soup: BeautifulSoup):
        tag = soup.select_one(".summary_image a img")
        if isinstance(tag, Tag):
            if tag.has_attr("data-src"):
                self.novel_cover = self.absolute_url(tag["data-src"])
            elif tag.has_attr("src"):
                self.novel_cover = self.absolute_url(tag["src"])

    def parse_authors(self, soup: BeautifulSoup):
        self.novel_author = ", ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )

    def get_chapter_list_soup(self, soup: BeautifulSoup) -> BeautifulSoup:
        nl_id = soup.select_one('[id^="manga-chapters-holder"][data-id]')
        if isinstance(nl_id, Tag):
            response = self.submit_form(
                f"{self.home_url}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": nl_id["data-id"],
                },
            )
        else:
            clean_novel_url = self.novel_url.split("?")[0].strip("/")
            response = self.submit_form(f"{clean_novel_url}/ajax/chapters/")
        return self.make_soup(response)

    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for a in reversed(soup.select("ul.main .wp-manga-chapter > a")):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip(),
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> None:
        soup = self.get_soup(chapter.url)
        contents = soup.select_one("div.reading-content")
        for img in contents.select("img"):
            if img.has_attr("data-src"):
                img.attrs = {"src": img["data-src"]}
        return self.cleaner.extract_contents(contents)
