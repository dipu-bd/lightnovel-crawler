# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = (
    "https://lightnovelbastion.com/?s=%s&post_type=wp-manga&author=&artist=&release="
)


class LightNovelBastion(Crawler):
    base_url = "https://lightnovelbastion.com/"

    def initialize(self) -> None:
        self.init_executor(1)
        self.cleaner.bad_tags.update(
            [
                "h3",
                "blockquote",
            ]
        )
        self.cleaner.bad_css.update([".lnbad-tag"])

    def search_novel(self, query):
        query = quote_plus(query.lower())
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content")[:20]:
            a = tab.select_one(".post-title h4 a")
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

        possible_title = soup.select_one(".post-title h3")
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".summary_image a img")["data-src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        if len(soup.select("ul.version-chap li.has-child li.wp-manga-chapter")):
            logger.debug("Has volume definitions")
            for li in reversed(soup.select("ul.version-chap li.has-child")):
                vol_id = len(self.volumes) + 1
                vol_title = li.select_one("a.has-child").text.strip()
                self.volumes.append(
                    {
                        "id": vol_id,
                        "title": vol_title,
                    }
                )
                for a in reversed(li.select("ul.sub-chap li.wp-manga-chapter a")):
                    chap_id = len(self.chapters) + 1
                    self.chapters.append(
                        {
                            "id": chap_id,
                            "volume": vol_id,
                            "title": a.text.strip(),
                            "url": self.absolute_url(a["href"]),
                        }
                    )
        else:
            logger.debug("Has no volume definitions")
            for a in reversed(soup.select(".wp-manga-chapter a")):
                self.chapters.append(
                    {
                        "id": len(self.chapters) + 1,
                        "title": a.text.strip(),
                        "url": self.absolute_url(a["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".reading-content .text-left")
        return self.cleaner.extract_contents(contents)
