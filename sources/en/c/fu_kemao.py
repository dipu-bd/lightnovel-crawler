# -*- coding: utf-8 -*-
import logging
from base64 import b64decode
from urllib.parse import quote_plus

from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = b64decode(
    "aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8/cG9zdF90eXBlPW5vdmVsJnM9".encode()
).decode()


class Fu_kCom_ademao(Crawler):
    has_mtl = True
    base_url = b64decode("aHR0cHM6Ly9jb21yYWRlbWFvLmNvbS8=".encode()).decode()

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["header"])
        self.cleaner.bad_css.update(
            [
                "#ad",
                "#bookmark" "#div-gpt-ad-comrademaocom35917",
                "#div-gpt-ad-comrademaocom35918",
            ]
        )

    def search_novel(self, query):
        url = novel_search_url + quote_plus(query)
        # logger.debug('Visiting: ' + url)
        soup = self.get_soup(url)

        results = []
        for a in soup.select("#novel a"):
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )
        return results

    def read_novel_info(self):
        # logger.debug('Visiting %s', self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.rsplit(r"\u2013", 1)[0].strip()
        logger.debug("Novel title = %s", self.novel_title)

        possible_image = soup.select_one(
            "img.attachment-post-thumbnail, .seriedetailcontent img"
        )
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # self.novel_author = soup.select_one('#Publisher a')['href']
        # logger.info('Novel author: %s', self.novel_author)

        logger.info("Getting chapters...")
        chapter_links = soup.select("#chapterlist li a")
        paginations = soup.select(".pagination-list .pagination-link")
        if len(chapter_links):
            volumes = set()
            for a in reversed(chapter_links):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                volumes.add(vol_id)
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "url": self.absolute_url(str(a["href"])),
                        "title": a.text.strip(),
                    }
                )
        elif len(paginations):
            pagination = paginations[-1]
            page_count = int(pagination.text) if isinstance(pagination, Tag) else 1
            logger.info("# page count: %d", page_count)

            futures_to_check = []
            novel_url = self.novel_url.split("?")[0].strip("/")
            for i in range(page_count - 1):
                future = self.executor.submit(
                    self.get_soup, novel_url + "/page/%d" % (page_count - i)
                )
                futures_to_check.append(future)
            futures_to_check.append(self.executor.submit(lambda: soup))

            volumes = set()
            for future in futures_to_check:
                soup = future.result()
                for a in reversed(soup.select(".container table a")):
                    chap_id = len(self.chapters) + 1
                    vol_id = len(self.chapters) // 100 + 1
                    volumes.add(vol_id)
                    self.chapters.append(
                        {
                            "id": chap_id,
                            "volume": vol_id,
                            "url": self.absolute_url(str(a["href"])),
                            "title": a.text.strip(),
                        }
                    )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        body = soup.select_one("#content, #chaptercontent")
        return self.cleaner.extract_contents(body)
