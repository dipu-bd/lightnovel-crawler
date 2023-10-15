# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
from urllib.parse import quote_plus

logger = logging.getLogger(__name__)

search_url = "/index.php?s=so&module=book&keyword="


class NovelHallCrawler(Crawler):
    base_url = [
        "https://www.novelhall.com/",
        "http://www.novelhall.com/",
        "https://novelhall.com/",
        "http://novelhall.com/",
    ]

    has_manga = False
    has_mtl = True

    def search_novel(self, query: str):
        soup = self.get_soup(self.absolute_url(search_url + quote_plus(query.lower())))

        results = []
        for novel in soup.select('.section3 table tbody tr'):
            novel = novel.findAll('a')
            novel_link = novel[1]
            latest_chapter = novel[2].text.strip().split('.')
            chapter_number = latest_chapter[0]

            if chapter_number.isdigit():
                latest_chapter = "Chapter %s: %s" % (chapter_number, latest_chapter[1])
            else:
                latest_chapter = "Latest chapter: " + latest_chapter[0]

            results.append(
                {
                    "title": novel_link.text.strip(),
                    "url": self.absolute_url(novel_link['href']),
                    "info": latest_chapter
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        if soup is None:
            raise LookupError("novel url is invalid.")

        book_info = soup.select_one("div.book-info")

        self.novel_title = book_info.h1.text
        assert self.novel_title, "no novel title"
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.book-img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

            if possible_image['src'] == "":
                logger.warning("Novel cover: unavailable")
            else:
                logger.info("Novel cover: %s", self.novel_cover)
        else:
            logger.info("Novel cover: unavailable")

        author = soup.select("div.book-info div.total.booktag span.blue")[0]
        author.select_one("p").extract()
        self.novel_author = author.text.replace("Author：", "").strip()
        logger.info("Novel author: %s", self.novel_author)

        self.novel_tags = [soup.select_one("div.book-info div.total.booktag a.red").text.strip()]
        logger.info("Novel tags: %s", self.novel_tags)

        synopsis = soup.select_one(".js-close-wrap")
        if synopsis:
            synopsis.select_one(".blue").extract()
            self.novel_synopsis = self.cleaner.extract_contents(synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for a in soup.select("div#morelist.book-catalog ul li a"):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div#htmlContent.entry-content")
        for ads in contents.select("div"):
            ads.extract()

        return str(contents)
