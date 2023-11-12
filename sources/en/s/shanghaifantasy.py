# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Shanghaifantasy(Crawler):
    base_url = ["https://shanghaifantasy.com/"]
    wp_json_novel = "https://shanghaifantasy.com/wp-json/wp/v2/novel/%s"
    wp_json_chapters = "https://shanghaifantasy.com/wp-json/fiction/v1/chapters?category=%s&order=asc&per_page=%%s"

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        novel_id = soup.select_one("div#likebox").attrs["data-novel"]
        total_chapters = soup.select("div.grid p.text-sm")[1].text.split(": ")[1]
        get_novel_json = self.get_response(self.wp_json_novel % novel_id).json()

        novel_title = get_novel_json["title"]["rendered"]
        self.novel_title = novel_title

        novel_author = soup.select("div.grid p.text-sm")[2].text
        if "Author" in novel_author:
            self.novel_author = novel_author.split(": ")[1]

        novel_synopsis = soup.select_one("div[x-show*='Synopsis']").get_text()
        self.novel_synopsis = novel_synopsis

        novel_cover = soup.select_one("img[class*='object-cover']")["src"]
        self.novel_cover = novel_cover

        novel_chap_id = get_novel_json["categories"][0]
        chapters = self.get_response(self.wp_json_chapters % novel_chap_id % total_chapters).json()
        for chapter in chapters:
            chap_id = 1 + len(self.chapters)
            locked = chapter["locked"]

            if not locked:
                self.chapters.append(
                    {
                        "id": chap_id,
                        "title": chapter["title"],
                        "url": chapter["permalink"]
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("div.contenta")
        return self.cleaner.extract_contents(content)
