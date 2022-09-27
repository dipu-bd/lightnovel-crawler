# -*- coding: utf-8 -*-
import logging
import re


from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

novel_search_url = "%ssearch.aspx?k=%s"
chapter_list_url = "%s&page=%d"


class UukanshuOnline(Crawler):
    base_url = ["https://sj.uukanshu.com/"]

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(novel_search_url % (self.home_url, query))
        results = []

        for data in soup.select("#bookList li"):
            title = data.select_one(".book-title a.name")["title"]
            author = data.select_one(".book-title .aut").get_text()
            url = self.home_url + data.select_one(".book-title a.name")["href"]

            results.append(
                {
                    "title": title,
                    "url": url,
                    "info": f"Author: {author}",
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".bookname").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".book-info img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = (
            soup.select_one(".book-info dd").text.replace("作者：", "").strip()
        )
        logger.info("Novel author: %s", self.novel_author)

        logger.info("Getting chapters...")
        soup = self.get_soup(chapter_list_url % (self.novel_url, 1))
        try:
            last_page = soup.select_one(".pages a:last-child")
            page_count = int(re.findall(r"&page=(\d+)", str(last_page["href"]))[0])
        except Exception as err:
            logger.debug("Failed to parse page count. Error: %s", err)
            page_count = 0
        logger.info("Total pages: %d", page_count)

        futures = [
            self.executor.submit(self.get_soup, chapter_list_url % (self.novel_url, p))
            for p in range(2, page_count + 1)
        ]
        page_soups = [soup] + [f.result() for f in futures]

        for soup in page_soups:
            for a in soup.select("ul#chapterList li a"):
                chap_id = len(self.chapters) + 1
                vol_id = 1 + len(self.chapters) // 100
                if chap_id % 100 == 1:
                    self.volumes.append({"id": vol_id})
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": a.text,
                        "url": self.home_url + a["href"],
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        body = soup.select_one("#bookContent")

        content = self.cleaner.extract_contents(body)

        return self.format_text(content)

    def format_text(self, text):
        text = re.sub(
            r"[UＵ][UＵ]\s*看书\s*[wｗ][wｗ][wｗ][\.．][uｕ][uｕ][kｋ][aａ][nｎ][sｓ][hｈ][uｕ][\.．][cｃ][oｏ][mｍ]",
            "",
            text,
        )
        text = text.replace("章节缺失、错误举报", "")
        text = text.replace("注：如你看到本章节内容是防盗错误内容、本书断更等问题请登录后→→", "")
        text = text.replace("最新网址：", "")
        text = text.replace("请记住本书首发域名：。手机版更新最快网址：", "")
        text = text.replace("www.uukanshu.com", "")
        return text
