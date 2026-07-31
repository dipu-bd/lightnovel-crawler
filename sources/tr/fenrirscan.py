# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, LegacyCrawler, SearchResult

logger = logging.getLogger(__name__)


class FenrirScans(LegacyCrawler):
    base_url = ["https://fenrirscans.com/"]
    search_url = "https://fenrirscans.com/wp-admin/admin-ajax.php"
    has_manga = False
    has_mtl = False

    def search_novel(self, query):
        # The site no longer answers this: its theme registers only next/prev/tepki, and
        # `ts_ac_do_search` returns `400`. Its `?s=` page is no better — the grid it
        # renders is byte-identical for every query, including one that matches nothing.
        # Left in place because a restored endpoint would work again as written, and
        # returning nothing is what this did before the request began raising.
        data = {
            "action": "ts_ac_do_search",
            "ts_ac_query": query,
        }
        try:
            response = self.post_response(self.search_url, data=data)
            return [
                SearchResult(
                    title=item["post_title"],
                    url=self.absolute_url(item["post_link"]),
                )
                for item in response.json().get("series", [])[0].get("all", [])
            ]
        except Exception:
            return []

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        # Metadata
        title = soup.find("h1")
        if title:
            self.novel_title = title.text.strip()

        # Synopsis
        summary = soup.find("div", {"class": "entry-content"})
        if summary:
            self.novel_synopsis = self.cleaner.extract_contents(summary)

        # Cover
        cover = soup.find("img", {"class": "wp-post-image"})
        if cover:
            self.novel_cover = self.absolute_url(cover.get("src"))
        # Tags/Genres
        for tag in soup.select('a[rel="tag"]'):
            self.novel_tags.append(tag.text)

        # Author
        author = soup.find("a", href=re.compile(r"/authors/"))
        if author:
            self.novel_author = author.text.strip()

        # Chapters
        chapter_links = soup.find_all("a", href=re.compile(r"-bolum-\d+"))

        # Reverse so earliest chapters first
        chapter_links = list(reversed(chapter_links))

        for idx, a in enumerate(chapter_links, 1):
            chap_url = self.absolute_url(a["href"])
            chap_title = (a.find("span", {"class": "chapternum"}) or a).text
            self.chapters.append(
                Chapter(
                    id=idx,
                    url=chap_url,
                    title=chap_title,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.find("div", {"id": "readerarea"})
        return self.cleaner.extract_contents(content)
