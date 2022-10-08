# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures
from lncrawl.core.crawler import Crawler
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
search_url = "https://www.newsnovel.net/search/%s"


class NewsNovelCrawler(Crawler):
    base_url = "https://www.newsnovel.net/"

    # NOTE: Disabled because search doesn't work on site.
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)
    #     results = []
    #     for tab in soup.select('.home-truyendecu')[:20]:
    #         search_title = tab.select_one('a')
    #         latest = tab.select_one('.caption .label-primary').text.strip()
    #         results.append({
    #             'title': search_title['title'].strip(),
    #             'url': self.absolute_url(
    #                 tab.select_one('a')['href']),
    #             'info': 'Latest chapter: %s' % (latest)
    #         })
    #     return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one(".info-holder .book img")

        self.novel_title = image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        authors = soup.select('.info-holder .info a[href*="/authors/"]')
        self.novel_author = ", ".join([a.text.strip() for a in authors])
        logger.info("Novel author: %s", self.novel_author)

        novel_id = soup.select_one("#id_post")["value"]
        logger.info("Novel id: %s", novel_id)

        # This is copied from the Novelfull pagination 'hanlder' with minor tweaks
        pagination_links = soup.select(".pagination li a")
        pagination_page_numbers = []
        for pagination_link in pagination_links:
            pagination_page_numbers.append(int(pagination_link["data-page"]))

        page_count = max(pagination_page_numbers) if pagination_page_numbers else 0
        logger.info("Chapter list pages: %d" % page_count)

        logger.info("Getting chapters...")
        futures_to_check = {
            self.executor.submit(self.download_chapter_list, i + 1, novel_id): str(i)
            for i in range(page_count + 1)
        }
        [x.result() for x in futures.as_completed(futures_to_check)]

        # Didn't test without this, but with pagination the chapters could be
        # in different orders
        logger.info("Sorting chapters...")
        self.chapters.sort(key=lambda x: x["volume"] * 1000 + x["id"])

        # Copied straight from Novelfull
        logger.info("Adding volumes...")
        mini = self.chapters[0]["volume"]
        maxi = self.chapters[-1]["volume"]
        for i in range(mini, maxi + 1):
            self.volumes.append({"id": i})

    def download_chapter_list(self, page, novel_id):
        # Uses an AJAX based pagination that calls this address:
        pagination_url = "https://www.newsnovel.net/wp-admin/admin-ajax.php"

        url = pagination_url.split("?")[0].strip("/")
        # url += '?action=tw_ajax&type=pagination&id=%spage=%s' % (novel_id, page)
        soup = BeautifulSoup(
            self.submit_form(
                url,
                {
                    "action": "tw_ajax",
                    "type": "pagination",
                    "id": novel_id,
                    "page": page,
                },
            ).json()["list_chap"],
            "lxml",
        )

        if not soup.find("body"):
            raise ConnectionError("HTML document was not loaded properly")

        for a in soup.select("ul.list-chapter li a"):
            title = a.text.strip()

            chapter_id = len(self.chapters) + 1
            match = re.findall(r"ch(apter)? (\d+)", title, re.IGNORECASE)
            if len(match) == 1:
                chapter_id = int(match[0][1])

            volume_id = 1 + (chapter_id - 1) // 100
            match = re.findall(r"(book|vol|volume) (\d+)", title, re.IGNORECASE)
            if len(match) == 1:
                volume_id = int(match[0][1])

            data = {
                "title": title,
                "id": chapter_id,
                "volume": volume_id,
                "url": self.absolute_url(a["href"]),
            }
            self.chapters.append(data)

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one(".chapter-c")
        for br in contents.select("br"):
            br.extract()

        return str(contents)
