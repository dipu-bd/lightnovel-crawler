# -*- coding: utf-8 -*-
import logging
import re

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LightNovelPub(Crawler):
    base_url = [
        "https://www.lightnovelpub.com/",
        "https://www.lightnovelworld.com/",
        "https://www.novelpub.com/",
    ]

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                ".adsbox",
                ".ad-container",
                "p > strong > strong",
                ".OUTBRAIN",
                "p[class]",
                ".ad",
                "p:nth-child(1) > strong",
                ".noveltopads",
                ".chadsticky",
            ]
        )

    def search_novel(self, query):
        soup = self.get_soup(f"{self.home_url}search")
        token_tag = soup.select_one(
            '#novelSearchForm input[name="__LNRequestVerifyToken"]'
        )
        assert token_tag, "No request verify token found"
        token = token_tag["value"]

        response = self.submit_form(
            f"{self.home_url}lnsearchlive",
            data={"inputContent": query},
            headers={
                "lnrequestverifytoken": token,
                "referer": f"{self.home_url}search",
            },
        )

        soup = self.make_soup(response.json()["resultview"])

        results = []
        for a in soup.select(".novel-list .novel-item a"):
            possible_info = a.select_one(".novel-stats")
            info = possible_info.text.strip() if possible_info else None
            results.append(
                {
                    "title": str(a["title"]).strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": info,
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        self.novel_url = soup.find("meta", property="og:url")["content"]

        possible_title = soup.select_one(".novel-info .novel-title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text.strip()

        possible_image = soup.select_one(".glass-background img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])

        possible_author = soup.select_one('.author a[href*="/author/"]')
        if isinstance(possible_author, Tag):
            self.novel_author = possible_author["title"]

        soup = self.get_soup(f"{self.novel_url}/chapters/page-1")
        try:
            last_page = soup.select_one(".PagedList-skipToLast a")
            if not last_page:
                paginations = soup.select('.pagination li a[href*="/chapters/page"]')
                last_page = paginations[-2] if len(paginations) > 1 else paginations[0]
            assert isinstance(last_page, Tag)
            page_count = int(re.findall(r"/page-(\d+)", str(last_page["href"]))[0])
        except Exception as err:
            logger.debug("Failed to parse page count. Error: %s", err)
            page_count = 0

        futures = [
            self.executor.submit(self.get_soup, f"{self.novel_url}/chapters/page-{p}")
            for p in range(2, page_count + 1)
        ]
        page_soups = [soup] + [f.result() for f in futures]

        for soup in page_soups:
            vol_id = len(self.volumes) + 1
            self.volumes.append({"id": vol_id})
            for a in soup.select("ul.chapter-list li a"):
                chap_id = len(self.chapters) + 1
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
        body = soup.select_one("#chapter-container")
        return self.cleaner.extract_contents(body)
