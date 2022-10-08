# -*- coding: utf-8 -*-
import logging
import re
from concurrent import futures


from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "http://boxnovel.org/search?keyword=%s"


class BoxNovelOrgCrawler(Crawler):
    base_url = [
        "http://boxnovel.org/",
        "https://boxnovel.org/",
    ]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".col-novel-main .list-novel .row"):
            search_title = tab.select_one(".novel-title a")
            latest = tab.select_one(".text-info a").text.strip()
            results.append(
                {
                    "title": search_title.text.strip(),
                    "url": self.absolute_url(tab.select_one(".novel-title a")["href"]),
                    "info": "Latest chapter: %s" % (latest),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        image = soup.select_one(".book img")

        self.novel_title = image["alt"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        author = soup.find_all(href=re.compile("author"))
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        # This is copied from the Novelfull pagination 'hanlder' with minor tweaks
        pagination_links = soup.select(".pagination li a")
        pagination_page_numbers = []
        for pagination_link in pagination_links:
            # Boxnovel.org pagination numbering boxes contain non-digit characters
            if pagination_link.text.isdigit():
                pagination_page_numbers.append(int(pagination_link.text))

        page_count = max(pagination_page_numbers) if pagination_page_numbers else 0
        logger.info("Chapter list pages: %d" % page_count)

        logger.info("Getting chapters...")
        futures_to_check = {
            self.executor.submit(
                self.download_chapter_list,
                i + 1,
            ): str(i)
            for i in range(page_count + 1)
        }
        [x.result() for x in futures.as_completed(futures_to_check)]

        # Didn't test without this, but with pagination the chapters could be in different orders
        logger.info("Sorting chapters...")
        self.chapters.sort(key=lambda x: x["volume"] * 1000 + x["id"])

        # Copied straight from Novelfull
        logger.info("Adding volumes...")
        mini = self.chapters[0]["volume"]
        maxi = self.chapters[-1]["volume"]
        for i in range(mini, maxi + 1):
            self.volumes.append({"id": i})

    def download_chapter_list(self, page):
        url = self.novel_url.split("?")[0].strip("/")
        url += "?page=%d&per-page=50" % page
        soup = self.get_soup(url)

        for a in soup.select("ul.list-chapter li a"):
            title = str(a["title"]).strip()

            chapter_id = len(self.chapters) + 1
            # match = re.findall(r'ch(apter)? (\d+)', title, re.IGNORECASE)
            # if len(match) == 1:
            #     chapter_id = int(match[0][1])
            # # end if

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
        contents = soup.select_one("div.chr-c, #chr-content")
        return self.cleaner.extract_contents(contents)
