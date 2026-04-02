# -*- coding: utf-8 -*-
from typing import Optional

from lncrawl.core import Chapter, Novel, PageSoup, Volume
from lncrawl.exceptions import LNException
from lncrawl.templates.wordpress import WordpressTemplate


class PhoenixNovels(WordpressTemplate):
    base_url = "https://phoenixnovels.com.br/"
    novel_author_selector = '.author-content a[href*="novel-author"]'
    auto_create_volumes = False

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                "div.padSection",
                "div#padSection",
            ]
        )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one("#manga-title h1")
        if not tag:
            raise LNException("Título da novel não encontrado com o seletor '#manga-title h1'.")
        for span in tag.select("span"):
            span.extract()
        novel.title = tag.text.strip()

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        image = soup.select_one(".summary_image img")
        if image:
            cover_url = image.get("data-src") or image.get("src")
            if cover_url:
                novel.cover_url = self.absolute_url(cover_url)

    def parse_search_item_info(self, soup: PageSoup) -> str:
        latest = soup.select_one(".latest-chap .chapter a")
        votes = soup.select_one(".rating .total_votes")
        return "%s | Rating: %s" % (
            latest.text.strip() if latest else "N/A",
            votes.text.strip() if votes else "0",
        )

    def parse_volume_list(self, soup: PageSoup, novel: Novel) -> None:
        novel.volumes = []
        novel.chapters = []
        chapter_list_url = self.absolute_url("ajax/chapters", novel.url)
        ch_soup = self.scraper.post_soup(chapter_list_url, headers={"accept": "*/*"})
        chap_id = 0
        volume_id = 0
        for li in reversed(ch_soup.select("li.parent.has-child")):
            volume_id += 1
            volume_title = li.select_one("a.has-child")
            if not volume_title:
                continue
            novel.volumes.append(Volume(id=volume_id, title=volume_title.text.strip()))
            for a in reversed(li.select(".wp-manga-chapter a[href]")):
                for span in a.find_all("span"):
                    span.extract()
                chap_id += 1
                novel.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=volume_id,
                        title=a.text.strip(),
                        url=self.absolute_url(a["href"]),
                    )
                )

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(self.build_chapter_url(chapter))
        contents: Optional[PageSoup] = soup.select_one(".reading-content") or soup.select_one(
            ".text-left"
        )
        if contents:
            self.parse_chapter_body(contents, chapter)
        else:
            chapter.body = ""
