import logging
import re
from typing import List

from lncrawl.core import Chapter, LegacyCrawler, SearchResult, Volume

logger = logging.getLogger(__name__)

search_url = "https://www.banxia.cc/modules/article/search_t.php"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:128.0) Gecko/20100101 Firefox/128.0",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://www.banxia.cc",
    "Referer": "https://www.banxia.cc/",
    "Cookie": "jieqiUserCharset=utf-8;",
}


class Xbanxia(LegacyCrawler):
    base_url = ["https://www.xbanxia.com/", "https://www.banxia.cc/"]
    has_manga = False
    has_mtl = False

    def search_novel(self, query: str) -> List[SearchResult]:
        logger.debug(f"Searching {query} on Xbanxia")

        # The search URL redirect to the closest match instead of a list of results
        data = {"searchkey": f"{query}", "Submit": ""}
        soup = self.post_soup(
            search_url,
            data,
            headers,
        )

        title = soup.select_one("div.book-describe h1").text
        if not title:
            return []

        last_update = ""
        for p in soup.select("div.book-describe p"):
            if p.text.startswith("最近更新︰"):
                last_update = p.text.replace("最近更新︰", "").strip()
                break

        last_chapter = ""
        for p in soup.select("div.book-describe p"):
            if p.text.startswith("最新章節︰"):
                last_chapter = p.text.replace("最新章節︰", "").strip()
                break

        canonical_link = soup.select_one("link[rel='canonical']")
        if canonical_link and "href" in canonical_link.attrs:
            novel_url = canonical_link["href"]
        else:
            novel_url = self.absolute_url(soup.select_one("div.book-describe a")["href"])

        chapter_count = len(soup.select("div.book-list ul li a"))

        return [
            SearchResult(
                title=title,
                url=novel_url,
                info=f"Chapters: {chapter_count} | Latest: {last_chapter} | Last update: {last_update}",
            )
        ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.book-describe h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        author = soup.find_all(href=re.compile("author"))
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(soup.select_one("div.book-img img")["data-original"])
        logger.info("Novel cover: %s", self.novel_cover)

        for possible_genre in soup.select("div.book-describe p"):
            if possible_genre.text.startswith("類型︰"):
                self.novel_tags.append(possible_genre.text.replace("類型︰", "").strip())
        logger.info("Novel tags: %s", self.novel_tags)

        possible_synopsis = soup.select_one("div.book-describe .describe-html")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for div in soup.select("div.book-list ul li"):
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append(Volume(id=vol_id))

            for a in div.select("a"):
                ch_id = len(self.chapters) + 1
                self.chapters.append(
                    Chapter(
                        id=ch_id,
                        volume=vol_id,
                        title=a.text,
                        url=self.absolute_url(a["href"]),
                    )
                )

        logger.debug("%d chapters and %d volumes found", len(self.chapters), len(self.volumes))

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div#nr1")
        return str(contents)
