# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novel27.com/?s=%s&post_type=wp-manga&author=&artist=&release="


class Novel27(Crawler):
    base_url = "https://novel27.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content")[:20]:
            a = tab.select_one(".post-title h3 a")
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
            soup.select_one(".summary_image a img")["data-src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [a.text.strip() for a in soup.select('.author-content a[href*="authors"]')]
        )
        logger.info("%s", self.novel_author)

        volumes = set()
        chapters = soup.select("ul.main li.wp-manga-chapter a")
        for a in reversed(chapters):
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.text-left")
        for bad in contents.select("h3, .code-block, script, .adsbygoogle"):
            bad.extract()

        return self.cleaner.extract_contents(contents)
