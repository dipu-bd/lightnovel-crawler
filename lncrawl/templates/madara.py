from typing import Dict, List
from urllib.parse import quote

from bs4 import BeautifulSoup, Tag

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException


class MadaraTemplate(Crawler):
    is_template = True

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def search_novel(self, query) -> List[Dict[str, str]]:
        query = quote(query.lower())
        url = f"{self.home_url}?s={query}&post_type=wp-manga&author=&artist=&release="
        soup = self.get_soup(url)
        self.parse_search_results(soup)
        return [
            self.parse_search_item(tab) for tab in soup.select(".c-tabs-item__content")
        ]

    def parse_search_item(self, tab: Tag) -> Dict[str, str]:
        a = tab.select_one(".post-title h3 a")
        latest = tab.select_one(".latest-chap .chapter a").text
        votes = tab.select_one(".rating .total_votes").text
        return {
            "title": a.text.strip(),
            "url": self.absolute_url(a["href"]),
            "info": "%s | Rating: %s" % (latest, votes),
        }

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)
        self.parse_title(soup)
        self.parse_image(soup)
        self.parse_authors(soup)
        self.parse_chapter_list(soup)
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
            self.novel_id = nl_id["data-id"]
            response = self.submit_form(
                f"{self.home_url}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": self.novel_id,
                },
            )
        else:
            clean_novel_url = self.novel_url.split("?")[0].rstrip("/")
            response = self.submit_form(f"{clean_novel_url}/ajax/chapters/")
        return self.make_soup(response)

    def parse_chapter_list(self, soup: BeautifulSoup) -> None:
        for a in reversed(soup.select(".wp-manga-chapter a")):
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter) -> None:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.reading-content")
        for img in contents.select("img"):
            if img.has_attr("data-src"):
                img.attrs = {"src": img["data-src"]}
        return self.cleaner.extract_contents(contents)
