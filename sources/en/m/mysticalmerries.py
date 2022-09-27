# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://mysticalmerries.com/?s=%s"


class MysticalMerries(Crawler):
    base_url = "https://mysticalmerries.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-blog_item"):
            a = tab.select_one(".post-title h4 a")
            latest = "N/A"
            votes = "0"
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

        possible_image = soup.select_one(".summary_image a img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [a.text.strip() for a in soup.select(".author-content a")]
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

        contents = soup.select_one(".text-left")
        for bad in contents.select(".code-block, script, .adsbygoogle"):
            bad.extract()

        for images in contents.select("img"):
            images.extract()

        for junk in contents.select("p"):
            for bad in [
                "Want the next chapter? Click here:",
                "<a>https://ko-fi.com/milkywaytranslations</a>",
                "Want the next chapter?",
                "<a>Click here!</a>",
            ]:
                if bad in junk.text:
                    junk.extract()

        return self.cleaner.extract_contents(contents)
