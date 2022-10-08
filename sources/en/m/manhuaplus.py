# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = (
    "https://manhuaplus.online/?s=%s&post_type=wp-manga&author=&artist=&release="
)
post_chapter_url = "https://manhuaplus.online/wp-admin/admin-ajax.php"


class ArNovelCrawler(Crawler):
    has_manga = True
    base_url = "https://manhuaplus.online/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select("div.c-tabs-item__content"):
            a = tab.select_one("div.post-title h3 a")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (latest, votes),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".summary_image a img")["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="manga-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        self.novel_id = soup.select_one(
            ".wp-manga-action-button[data-action=bookmark]"
        )["data-post"]
        logger.info("Novel id: %s", self.novel_id)

        for span in soup.select(".page-content-listing span"):
            span.extract()

        logger.info("Sending post request to %s", post_chapter_url)
        response = self.submit_form(
            post_chapter_url,
            data={"action": "manga_get_chapters", "manga": int(self.novel_id)},
        )
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter > a")):
            chap_id = len(self.chapters) + 1
            vol_id = chap_id // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        if "Chapter" in soup.select_one("h1").text:
            chapter["title"] = soup.select_one("h1").text

        contents = soup.select_one("div.reading-content")

        for img in contents.findAll("img"):
            if img.has_attr("data-src"):
                src_url = img["data-src"]
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        return self.cleaner.extract_contents(contents)
