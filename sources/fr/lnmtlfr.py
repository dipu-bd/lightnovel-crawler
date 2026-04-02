# -*- coding: utf-8 -*-
from urllib.parse import urlencode

from lncrawl.core import Chapter, Novel, PageSoup, Volume
from lncrawl.templates.wordpress import WordpressTemplate


class Lnmtlfr(WordpressTemplate):
    base_url = ["https://lnmtlfr.com/"]
    has_mtl = True
    chapter_body_selector = "div.text-left"
    auto_create_volumes = False
    search_item_list_selector = "div.row.c-tabs-item__content"

    def build_search_url(self, query: str) -> str:
        return f"{self.scraper.origin}?{urlencode({'s': query.replace(' ', '+'), 'post_type': 'wp-manga'})}"

    def parse_search_item_title(self, soup: PageSoup) -> str:
        a = soup.select_one("div.post-title a")
        return a.text if a else ""

    def parse_search_item_url(self, soup: PageSoup) -> str:
        a = soup.select_one("div.post-title a")
        return self.absolute_url(a.get("href")) if a else ""

    def parse_search_item_info(self, soup: PageSoup) -> str:
        item = soup.select_one("div.post-content_item.mg_author div.summary-content")
        if not item:
            return ""
        authors = item.select("a")
        author_names = ", ".join([a.text for a in authors])
        return f"Author{'s' if len(authors) > 1 else ''}: {author_names}"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        h1 = soup.select_one("div.post-title h1")
        novel.title = h1.text.strip() if h1 else ""

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        img = soup.select_one("div.summary_image img")
        if img and img.get("src"):
            novel.cover_url = self.absolute_url(img["src"])

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        p = soup.select_one("div.summary__content p")
        novel.synopsis = self.cleaner.extract_contents(p) if p else ""

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        ac = soup.select_one("div.author-content")
        if ac:
            novel.author = ", ".join(e.text.strip() for e in ac.select("a"))

    def parse_volume_list(self, soup: PageSoup, novel: Novel) -> None:
        novel.volumes = []
        novel.chapters = []
        novel.language = "fr"
        rating = soup.select_one("input.rating-post-id")
        if not rating or not rating.get("value"):
            return
        nid = rating["value"]
        resp = self.scraper.submit_form(
            f"{self.scraper.origin}wp-admin/admin-ajax.php",
            data=f"action=manga_get_chapters&manga={nid}",
        )
        ch_soup = self.scraper.make_soup(resp)
        list_vol = ch_soup.select("ul.sub-chap.list-chap")
        if list_vol:
            for vol in reversed(list_vol):
                vol_id = len(novel.volumes) + 1
                novel.volumes.append(Volume(id=vol_id))
                for chap in reversed(vol.find_all("li")):
                    a = chap.find("a")
                    if not a:
                        continue
                    novel.chapters.append(
                        Chapter(
                            id=len(novel.chapters) + 1,
                            volume=vol_id,
                            title=a.text,
                            url=self.absolute_url(a.get("href")),
                        )
                    )
        else:
            novel.volumes.append(Volume(id=1))
            for chap in reversed(ch_soup.find_all("li")):
                a = chap.find("a")
                if not a:
                    continue
                novel.chapters.append(
                    Chapter(
                        id=len(novel.chapters) + 1,
                        volume=1,
                        title=a.text,
                        url=self.absolute_url(a.get("href")),
                    )
                )
