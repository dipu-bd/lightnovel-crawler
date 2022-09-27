# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = (
    "https://www.worldnovel.online/wp-json/writerist/v1/novel/search?keyword=%s"
)
chapter_list_url = "https://www.worldnovel.online/wp-json/novel-id/v1/dapatkan_chapter_dengan_novel?category=%s&perpage=100&order=ASC&paged=%s"


class WorldnovelonlineCrawler(Crawler):
    base_url = "https://www.worldnovel.online/"

    # Disabled because it takes too long to respond
    # def search_novel(self, query):
    #     data = self.get_json(search_url % quote(query))
    #     results = []
    #     for item in data:
    #         results.append({
    #             'url': item['permalink'],
    #             'title': item['post_title'],
    #         })
    #     # end for
    #     return results
    # # end def

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".section-novel .breadcrumb-item.active")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('.section-novel img[alt^="Thumbnail"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["data-src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one('a[href*="/authorr/"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        # path = urllib.parse.urlsplit(self.novel_url)[2]
        # book_id = path.split('/')[2]
        # book_id = soup.select_one('span.js-add-bookmark')['data-novel']
        book_id = soup.select_one("body")
        assert isinstance(book_id, Tag)
        book_id = book_id["attr"]
        logger.info("Bookid = %s" % book_id)

        total_pages = len(soup.select("div.d-flex div.jump-to.mr-2"))

        futures = []
        for page in range(total_pages):
            url = chapter_list_url % (book_id, page + 1)
            f = self.executor.submit(self.get_json, url)
            futures.append(f)

        chapters = []
        for f in futures:
            chapters += f.result()

        for item in chapters:
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": item["permalink"],
                    "title": item["post_title"],
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one(
            ", ".join(
                [
                    ".entry-content",
                    ".post-content",
                    ".post-body",
                    "#content",
                    ".post",
                ]
            )
        )
        assert isinstance(contents, Tag)

        for div in contents.select("div.code-block"):
            div.extract()

        text = str(contents)
        text = text.replace("www.worldnovel.online", "")
        return text
