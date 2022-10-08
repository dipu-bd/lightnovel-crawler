# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import quote

from bs4.element import Tag
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

SEARCH_URL = "https://mtlreader.com/search"
CHAPTER_DETAIL_API = "https://www.mtlreader.com/api/chapter-content/%s"


class MtlReaderCrawler(Crawler):
    has_mtl = True
    base_url = [
        "https://mtlreader.com/",
        "https://www.mtlreader.com/",
    ]

    def search_novel(self, query):
        soup = self.get_soup(self.home_url)

        form_data = {}
        for input in soup.select('form[action$="/search"] input'):
            form_data[input["name"]] = input.get("value", "")
        form_data["input"] = quote(query)
        logger.debug("Form data: %s", form_data)

        response = self.submit_form(SEARCH_URL, form_data)
        soup = self.make_soup(response)

        results = []
        for div in soup.select(".property_item .proerty_text"):
            a = div.select_one("a")
            info = div.select_one("p.text-muted")
            assert isinstance(a, Tag)
            assert isinstance(info, Tag)
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info.text.strip() if info else "",
                }
            )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        novel_title_elem = soup.select_one(".agent-title")
        assert isinstance(novel_title_elem, Tag)
        self.novel_title = novel_title_elem.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        novel_image_elem = soup.select_one('meta[property="og:image"]')
        if isinstance(novel_image_elem, Tag):
            self.novel_cover = self.absolute_url(novel_image_elem["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.select_one(".agent-p-contact .fa.fa-user")
        if isinstance(possible_author, Tag) and isinstance(possible_author.parent, Tag):
            self.novel_author = possible_author.parent.text.strip()
            self.novel_author = re.sub(r"Author[: ]+", "", self.novel_author)
        logger.info("Novel author: %s", self.novel_author)

        for a in soup.select('table td a[href*="/chapters/"]'):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            chap_title = re.sub(r"^(\d+[\s:\-]+)", "", a.text.strip())
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": chap_title,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        self.get_response(chapter["url"])

        xsrf_token = self.cookies.get("XSRF-TOKEN")
        logger.debug("XSRF Token: %s", xsrf_token)

        chapter_id = re.findall(r"/chapters/(\d+)", chapter["url"])[0]
        url = CHAPTER_DETAIL_API % chapter_id
        logger.debug("Visiting: %s", url)

        response = self.get_response(
            url,
            headers={
                "referer": chapter["url"],
                "x-xsrf-token": xsrf_token,
                "accept": "application/json, text/plain, */*",
            },
        )
        text = re.sub("([\r\n]?<br>[\r\n]?)+", "\n\n", response.json())
        return "\n".join(["<p>" + x.strip() + "</p>" for x in text.split("\n\n")])
