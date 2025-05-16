# -*- coding: utf-8 -*-
import logging
from typing import List

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult

logger = logging.getLogger(__name__)


class LiteroticaCrawler(Crawler):
    base_url = ["https://www.literotica.com/"]

    def initialize(self) -> None:
        self.init_executor(ratelimit=2)

    def search_novel(self, query) -> List[SearchResult]:
        soup = self.get_soup(
            f"https://search.literotica.com/?query={query}", timeout=50
        )
        results = []
        for item in soup.select("div.panel.ai_gJ > div.ai_iG > a.ai_ii"):
            results.append(SearchResult(title=item.text.strip(), url=item["href"]))
        return results

    def read_novel_info(self) -> None:
        soup = self.get_soup(
            self.novel_url.replace("www.", "speedy.", 1), timeout=50, verify=False
        )
        isSeries = "/series/" in self.novel_url
        seriesLink = soup.select_one("a.bn_av")
        self.novel_cover = soup.select_one("a.y_eR > img")["src"] or None

        if isSeries or seriesLink:
            if seriesLink:
                soup = self.get_soup(
                    seriesLink["href"].replace("www.", "speedy.", 1),
                    timeout=50,
                    verify=False,
                )

            self.novel_title = soup.select_one("h1.j_bm").text
            self.novel_author = soup.select_one("a.y_eU").text
            self.novel_synopsis = soup.select_one("p.j_bq").text + "".join(
                " " + item.text for item in soup.select("p.bn_an")
            )
            self.novel_tags = [item.text for item in soup.select("a.av_as")]
            for item in soup.select("a.br_rj"):
                self.chapters.append(
                    dict(id=len(self.chapters) + 1, title=item.text, url=item["href"])
                )
        else:
            self.novel_title = soup.select_one("h1.headline").text
            self.novel_author = soup.select_one("a.y_eU").text
            self.novel_synopsis = soup.select_one("div.bn_B").text
            self.novel_tags = [item.text for item in soup.select("a.av_as")]
            self.chapters.append(dict(id=1, title=self.novel_title, url=self.novel_url))

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(
            f"{chapter['url'].replace('www.', 'speedy.', 1)}", timeout=50, verify=False
        )
        chapterText = ""
        while 1:
            chapterText += self.cleaner.extract_contents(soup.select_one("div.aa_ht"))
            try:
                nextUrl = (
                    "https://speedy.literotica.com"
                    + soup.select_one("a.l_bJ.l_bL").attrs["href"]
                )
                soup = self.get_soup(nextUrl, timeout=100, verify=False)
            except Exception:
                break
        return chapterText.replace(
            '"/images/', '"https://speedy.literotica.com/images/'
        ).replace(
            "https://www.literotica.com/images/",
            "https://speedy.literotica.com/images/",
        )
