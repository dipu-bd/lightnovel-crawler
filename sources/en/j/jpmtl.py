# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, Novel, PageSoup, SoupTemplate, Volume

logger = logging.getLogger(__name__)

book_url = "https://jpmtl.com/books/%s"
chapters_url = (
    "https://jpmtl.com/v2/chapter/%s/list?state=published&structured=true&direction=false"
)


class JpmtlCrawler(SoupTemplate):
    has_mtl = True
    base_url = "https://jpmtl.com/"

    def read_novel(self, novel: Novel) -> None:
        novel_id = novel.url.split("/")[-1]
        info_url = book_url % novel_id
        soup = self.scraper.get_soup(book_url % novel_id)

        novel.title = soup.select_one("h1.book-sidebar__title").text
        novel.cover_url = self.absolute_url(soup.select_one(".book-sidebar__img img").get("src"))
        novel.author = soup.select_one(".book-sidebar__author .book-sidebar__info").text

        novel.volumes = []
        novel.chapters = []
        toc = self.scraper.get_json(chapters_url % novel_id)
        for volume in toc:
            volume = novel.add_volume(
                id=volume["volume"],
                title=volume["volume_title"],
            )
            for chapter in volume["chapters"]:
                novel.add_chapter(
                    id=chapter["id"],
                    volume=volume.id,
                    title=chapter["title"],
                    url=self.absolute_url(f"{info_url}/{chapter['id']}"),
                )

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        contents = soup.select(".chapter-content__content p")
        body = [str(p) for p in contents if p.text.strip()]
        chapter.body = "<p>" + "</p><p>".join(body) + "</p>"
