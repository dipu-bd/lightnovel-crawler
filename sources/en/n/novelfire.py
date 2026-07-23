import logging
import re

from lncrawl.core import Chapter, LegacyCrawler, Volume
from lncrawl.core.models import SearchResult

logger = logging.getLogger(__name__)


class NovelFireCrawler(LegacyCrawler):
    search_url = "https://novelfire.net/search?keyword={}&type=title"
    base_url = [
        "https://novelfire.net/",
    ]
    has_mtl = False
    has_manga = False
    can_search = True
    request_rate_limit = 3

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1").text.strip()
        self.novel_author = soup.select_one('span[itemprop="author"]').text.strip()

        img = soup.select_one(".cover img")
        self.novel_cover = self.absolute_url(img["src"])

        vol_id = 1
        vol_url = self.novel_url + "/chapters"

        while vol_url:
            soup = self.get_soup(self.absolute_url(vol_url))

            chapters = soup.select("ul.chapter-list li a")
            for a in chapters:
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=vol_id,
                        title=a["title"],
                        url=self.absolute_url(a["href"]),
                    )
                )

            self.volumes.append(Volume(id=vol_id))

            next_vol_a = soup.select_one("a.page-link[rel='next']")
            if next_vol_a:
                vol_url = next_vol_a["href"]
                vol_id += 1
            else:
                vol_url = False
                break

    def download_chapter_body(self, chapter) -> str:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#content")
        if not contents:
            return ""

        # 1. Look through the very top elements inside the content container
        # We use a standard slice of the first 5 elements to completely isolate the headers
        elements_to_check = contents.find_all(True)[:5]

        for element in elements_to_check:
            element_text = element.get_text(" ", strip=True)
            if not element_text:
                continue

            # 2. checking for ANY title layout starting with "Chapter X"
            # This matches "Chapter 1:", "Chapter 1 –", "Chapter 1: Chapter 1:" etc.
            if re.match(r"(?i)^\s*chapter\s+\d+", element_text):
                element.decompose()

        return self.cleaner.extract_contents(contents)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(self.search_url.format(query))

        results = []
        for item in soup.select("ul.novel-list li.novel-item"):
            a = item.select_one("a")

            title = a.get("title")
            url = self.absolute_url(a.get("href"))

            chapters = a.select_one(".icon-book-open").text
            rank = a.select_one(".icon-crown").text
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    info=f"{chapters} | {rank}",
                )
            )

        return results
