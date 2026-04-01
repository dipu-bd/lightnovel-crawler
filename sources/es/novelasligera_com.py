# -*- coding: utf-8 -*-
import logging
from typing import Generator, Optional, Union

from bs4 import BeautifulSoup, Tag

from lncrawl.core import Chapter, Volume
from lncrawl.templates.soup.general import GeneralSoupTemplate

logger = logging.getLogger(__name__)


class NovelasLigeraCrawler(GeneralSoupTemplate):
    base_url = ["https://novelasligera.com/"]
    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        pass

    def get_novel_soup(self) -> BeautifulSoup:
        return super().get_novel_soup()

    def parse_title(self, soup: BeautifulSoup) -> str:
        h1 = soup.find("h1", class_="entry-title")
        return h1.get_text(strip=True) if h1 else ""

    def parse_cover(self, soup: BeautifulSoup) -> str:
        img = soup.select_one("div.elementor-widget-container img")
        if img:
            cover = img.get("data-lazy-src") or img.get("src")
            if cover and not cover.startswith("data:image/"):
                return cover

        og_image = soup.find("meta", property="og:image")
        return og_image.get("content", "") if og_image else ""

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for container in soup.find_all("div", class_="elementor-widget-container"):
            for p in container.find_all("p"):
                text = p.get_text(" ", strip=True)
                if "Autor:" in text:
                    author_text = text.split("Autor:", 1)[1].strip()
                    for author in [a.strip() for a in author_text.split(",") if a.strip()]:
                        yield author
                    return

    def parse_genres(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        for container in soup.find_all("div", class_="elementor-widget-container"):
            for p in container.find_all("p"):
                text = p.get_text(" ", strip=True)
                if "Género:" in text:
                    genres_text = text.split("Género:", 1)[1].strip().rstrip(".")
                    for genre in [g.strip() for g in genres_text.split(",") if g.strip()]:
                        yield genre
                    return

    def parse_summary(self, soup: BeautifulSoup) -> str:
        description = soup.find("meta", attrs={"name": "description"})
        if description and description.get("content"):
            return description["content"].strip()

        og_description = soup.find("meta", property="og:description")
        if og_description and og_description.get("content"):
            return og_description["content"].strip()

        return ""

    def parse_chapter_list(self, soup: BeautifulSoup) -> Generator[Union[Chapter, Volume], None, None]:
        seen_urls = set()
        chapter_id = 1

        selectors = [
            "div.elementor-tab-content ul.lcp_catlist li a",
            "div.elementor-accordion ul.lcp_catlist li a",
            "ul.lcp_catlist li a",
        ]

        for selector in selectors:
            found_any = False
            for a in soup.select(selector):
                url = a.get("href", "").strip()
                title = a.get_text(" ", strip=True)

                if not url or not title or url in seen_urls:
                    continue

                found_any = True
                seen_urls.add(url)

                chapter = Chapter(id=chapter_id)
                chapter.url = url
                chapter.title = title
                yield chapter
                chapter_id += 1

            if found_any:
                return

    def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        body = soup.select_one("div.entry-content[itemprop='text']") or soup.select_one("div.entry-content")
        if not body:
            return None

        for unwanted in body.select(
            ".osny-nightmode, "
            ".code-block, "
            ".zeno_font_resizer_container, "
            ".sharedaddy, "
            ".jp-relatedposts, "
            ".saboxplugin-wrap, "
            "script, style, noscript, iframe"
        ):
            unwanted.decompose()

        for unwanted in body.select(".post-ratings, .post-tags, .entry-meta, .author-box, .yarpp-related"):
            unwanted.decompose()

        return body

    def index_of_chapter(self, url: str) -> int:
        return super().index_of_chapter(url)
