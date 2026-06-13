# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core import Chapter, LegacyCrawler, SearchResult

logger = logging.getLogger(__name__)


class LightNovelPubOrg(LegacyCrawler):
    base_url = [
        "https://lightnovelpub.org/",
        "https://www.lightnovelpub.org/",
    ]

    def search_novel(self, query: str):
        url = f"api/search/?q={quote_plus(query.lower())}&search_type=title"
        novels = self.get_json(self.absolute_url(url))

        results = []
        for novel in novels["novels"]:
            novel_link = "novel/" + novel["slug"]
            latest = novel["latest_chapter_number"]
            info = f"Latest chapter: {latest}"

            results.append(
                SearchResult(
                    title=novel["title"],
                    url=self.absolute_url(str(novel_link)),
                    info=info,
                )
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        if soup is None:
            raise LookupError("novel url is invalid.")

        book_info = soup.select_one("div.novel-info")
        assert book_info, "No book info"

        possible_title = book_info.select_one("h1")
        assert possible_title, "No title tag"

        self.novel_title = possible_title.get_text(strip=True)

        possible_image = soup.select_one("div.novel-cover-container img[src]")
        if possible_image:
            self.novel_cover = self.absolute_url(str(possible_image["src"]))

        possible_novel_author = book_info.select_one("p.novel-author")
        if possible_novel_author:
            self.novel_author = possible_novel_author.get_text(strip=True)

        self.novel_tags = [a.get_text(strip=True) for a in book_info.select("div.genre-tags span")]

        synopsis = soup.select_one("div.summary-content")
        if synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(synopsis)

        possible_chapter_stat = soup.select_one("div.novel-stats-grid span.stat-value")
        total_chapters = int(possible_chapter_stat.get_text(strip=True))
        for i in range(1, total_chapters + 1):
            chapter_url = f"{self.novel_url}chapter/{i}"
            self.chapters.append(
                Chapter(
                    id=len(self.chapters),
                    url=chapter_url,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        possible_title = soup.select_one(".chapter-title")
        chapter.title = possible_title.get_text(strip=True)
        contents = soup.select_one("div.chapter-content")
        return self.cleaner.extract_contents(contents)
