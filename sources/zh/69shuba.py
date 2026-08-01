# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable
import urllib.parse

from lncrawl.core import Chapter, Novel, PageSoup, SearchResult, SoupTemplate

logger = logging.getLogger(__name__)
search_url = "https://www.69shuba.com/modules/article/search.php"


class sixnineshu(SoupTemplate):
    base_url = [
        "https://www.69shuba.com/",
        "https://www.69shu.com/",
        "https://www.69xinshu.com/",
        "https://www.69shu.pro/",
        "https://www.69shuba.pro/",
    ]
    request_rate_limit = 20

    novel_title_selector = "div.booknav2 h1"
    novel_cover_selector = "div.bookimg2 img"
    novel_author_selector = '.booknav2 p a[href*="author"]'
    novel_synopsis_selector = "div.navtxt"
    chapter_body_selector = "div.txtnav"

    def initialize(self) -> None:
        # lxml gives up on these pages once a novel runs past ~4.3k chapters
        self.parser = "html.parser"

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        query = urllib.parse.quote(query.encode("gbk"))
        soup = self.scraper.post_soup(
            search_url,
            data=f"searchkey={query}&submit=Search",
            encoding="gbk",
        )
        return soup.select("div.newbox ul li")

    def parse_search_item(self, soup: PageSoup) -> SearchResult:
        return SearchResult(
            title=soup.select_one("h3 a:not([imgbox])").text.title(),
            url=self.absolute_url(soup.select_one("a")["href"]),
            info="Latest: %s" % soup.select_one("div.zxzj p").text,
        )

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        return self.scraper.get_soup(self.absolute_url(novel.url), encoding="gbk")

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        match = re.search(r"tags:\s*'([^']+)'", str(soup))
        tags = match.group(1).split("|") if match else []
        tags += [a.text for a in soup.select('.booknav2 p a[href*="/class/"]')]
        novel.tags = [tag.strip() for tag in tags if tag.strip()]

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        url = self.absolute_url(novel.url).replace("/txt/", "/").replace(".htm", "/")
        catalog = self.scraper.get_soup(url, encoding="gbk")
        # The catalog lists newest first.
        for a in reversed(catalog.select("div#catalog ul li a")):
            novel.add_chapter(title=a.text.strip(), url=self.absolute_url(a["href"]))

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(self.build_chapter_url(chapter), encoding="gbk")
        body = soup.select_one(self.chapter_body_selector)
        for selector in ("h1", "div.txtinfo", "div#txtright"):
            tag = body.select_one(selector)
            if tag:
                tag.decompose()
        self.parse_chapter_body(body, chapter)
