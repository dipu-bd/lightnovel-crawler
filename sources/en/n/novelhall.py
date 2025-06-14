# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult, Volume

logger = logging.getLogger(__name__)


class NovelHallCrawler(Crawler):
    base_url = [
        "https://novelhall.com/",
        "https://www.novelhall.com/",
    ]

    has_manga = False
    has_mtl = True

    def search_novel(self, query: str):
        url = f"/index.php?s=so&module=book&keyword={quote_plus(query.lower())}"
        soup = self.get_soup(self.absolute_url(url))

        results = []
        for novel in soup.select(".section3 table tbody tr"):
            links = novel.select("a[href]")
            novel_link = links[1]

            latest = links[2].get_text(strip=True).split(".")
            if len(latest) == 2 and latest[0].isdigit():
                info = f"Chapter {latest[0]}: {latest[1]}"
            else:
                info = f"Latest chapter: {latest[0]}"

            results.append(
                SearchResult(
                    title=novel_link.get_text(strip=True),
                    url=self.absolute_url(str(novel_link["href"])),
                    info=info,
                )
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        if soup is None:
            raise LookupError("novel url is invalid.")

        book_info = soup.select_one("div.book-info")
        assert book_info, "no book info"

        possible_title = book_info.select_one('h1')
        assert possible_title, "no novel title"
        self.novel_title = possible_title.get_text(strip=True)

        possible_image = soup.select_one("div.book-img img[src]")
        if possible_image:
            self.novel_cover = self.absolute_url(str(possible_image["src"]))

        for span in book_info.select(".booktag span.blue"):
            key = r'Author：'
            text = span.get_text(strip=True)
            if key in text:
                self.novel_author = text.replace(key, "").strip()

        self.novel_tags = [
            a.get_text(strip=True)
            for a in book_info.select('.booktag a.red')
        ]

        synopsis = soup.select_one(".js-close-wrap")
        if synopsis:
            blue = synopsis.select_one(".blue")
            if blue:
                blue.extract()
            self.novel_synopsis = self.cleaner.extract_contents(synopsis)

        for a in soup.select("#morelist.book-catalog ul li a[href]"):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) < vol_id:
                self.volumes.append(Volume(id=vol_id))
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    url=self.absolute_url(a["href"]),
                    title=a.get_text(strip=True),
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#htmlContent.entry-content")
        return self.cleaner.extract_contents(contents)
