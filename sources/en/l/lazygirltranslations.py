# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LazyGirlTranslationsCrawler(Crawler):
    base_url = "https://lazygirltranslations.com/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "hr.wp-block-separator",
                'span[id^="ezoic-pub-ad"]',
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                "Table of Contents",
                "Next Chapter",
            ]
        )

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.entry-title")
        assert possible_title, "No title found"
        self.novel_title = possible_title.text.strip()

        cover_img = soup.select_one(".entry-content .wp-block-image img")
        if cover_img:
            src = cover_img.get("data-ezsrc") or cover_img.get("src")
            if src:
                self.novel_cover = self.absolute_url(src)

        first_p = soup.select_one(".inside-article .entry-content > p")
        if first_p:
            t = first_p.get_text(separator="\n", strip=True)
            author = next(filter(lambda x: "Author:" in x, t.split("\n")), "")
            self.novel_author = author.replace("Author: ", "")

        for a in soup.select(f'.wp-block-column a[href^="{self.home_url}"]'):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip(),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".entry-content")
        assert contents, "No contents found"
        return self.cleaner.extract_contents(contents)
