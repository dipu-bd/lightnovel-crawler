# -*- coding: utf-8 -*-
import logging
from bs4 import Tag
from lncrawl.core.crawler import Crawler
import urllib.parse

logger = logging.getLogger(__name__)


class EngNovel(Crawler):
    base_url = "https://engnovel.com/"

    def search_novel(self, query):
        soup = self.get_soup(
            f"https://engnovel.com/?s={urllib.parse.quote_plus(query)}"
        )

        results = []
        for novel in soup.select("div.caption"):
            latest = novel.select_one("small.btn-xs.label-primary")
            span_full = latest.select_one("span")
            if span_full:
                span_full.extract()

            results.append(
                {
                    "title": novel.select_one("a")["title"],
                    "url": self.absolute_url(novel.select_one("a")["href"]),
                    "info": latest.text,
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h3.title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # <div class="wallpaper" style=
        # "background:url(https://engnovel.com/wp-content/uploads/2019/07/lord-of-the-mysteries.jpeg) center no-repeat;background-size:cover"
        # >
        possible_image = soup.select_one("div.wallpaper")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(
                possible_image["style"].split("url(")[-1].split(")")[0]
            )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = ", ".join(
            [
                a.text.strip()
                for a in soup.select('div.info-chitiet a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        # <div class="desc-text" itemprop="description">
        #     <div class="short-content"><span class="glyphicon glyphicon-info-sign"></span> SUMMARY</div>
        #     <p>In the waves of steam and machinery...</p>
        #     <p>Firearms, cannons, battleships, airships...</p>
        #     <br>
        #     You can also read this novel here:
        #     <a target="_blank" href="https://enovelon.com">Read free novels online</a>
        # </div>
        synopsis = soup.select_one("div.desc-text")
        for e in synopsis.find_all():
            if e.name != "p":
                e.extract()

        for string in synopsis.strings:
            if string.strip() == "You can also read this novel here:":
                string.replace_with("")
                break

        self.novel_synopsis = self.cleaner.extract_contents(synopsis)
        logger.info("%s", self.novel_synopsis)

        # <a href="https://engnovel.com/action-novels" title="Action Novels" itemprop="genre">Action</a>
        self.novel_tags = [
            a.text.strip() for a in soup.select('div.info-chitiet a[itemprop="genre"]')
        ]
        logger.info("Tags: %s", self.novel_tags)

        novel_id = soup.select_one("#id_post")["value"]

        # <input name="total-page" type="hidden" value="36">
        for page in range(
            1, int(soup.select_one("input[name='total-page']")["value"]) + 1
        ):
            data = {
                "action": "tw_ajax",
                "type": "pagination",
                "id": novel_id,
                "page": page,
            }
            chapter_list = self.make_soup(
                self.post_response(
                    "https://engnovel.com/wp-admin/admin-ajax.php", data
                ).json()["list_chap"]
            )

            for a in chapter_list.select("ul.list-chapter li a"):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                if len(self.chapters) % 100 == 0:
                    self.volumes.append({"id": vol_id})
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": a["title"],
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.chapter-content")
        return self.cleaner.extract_contents(contents)
