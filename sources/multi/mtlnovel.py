# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "%s/wp-admin/admin-ajax.php?action=autosuggest&q=%s"


class MtlnovelCrawler(Crawler):
    has_mtl = True
    base_url = [
        "https://www.mtlnovel.com/",
        "https://id.mtlnovel.com/",
        "https://fr.mtlnovel.com/",
        "https://es.mtlnovel.com/",
        "http://www.mtlnovel.com/",
        "http://id.mtlnovel.com/",
        "http://fr.mtlnovel.com/",
        "http://es.mtlnovel.com/",
        "https://www.mtlnovels.com/",
        "https://id.mtlnovels.com/",
        "https://fr.mtlnovels.com/",
        "https://es.mtlnovels.com/",
        "http://www.mtlnovels.com/",
        "http://id.mtlnovels.com/",
        "http://fr.mtlnovels.com/",
        "http://es.mtlnovels.com/",
    ]

    def search_novel(self, query):
        query = query.lower().replace(" ", "%20")
        # soup = self.get_soup(search_url % query)

        results = []
        for url in self.base_url:
            list_url = search_url % (url, query)
            data = self.get_json(list_url)["items"][0]["results"]

            for item in data[:10]:
                url = item["permalink"]
                results.append(
                    {
                        "url": url,
                        "title": re.sub(r"</?strong>", "", item["title"]),
                    }
                )

        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("article .entry-title, h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".post-content amp-img[fallback]")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        try:
            self.novel_author = soup.select_one(
                'table.info a[href*="/novel-author/"]'
            ).text.strip()
        except Exception as e:
            logger.debug("Could not find novel author. %s", e)
        logger.info("Novel author: %s", self.novel_author)

        soup = self.get_soup(f"{self.novel_url}chapter-list/")
        for a in reversed(soup.select('.post-content .ch-list a.ch-link')):
            if self.novel_url not in a["href"]:
                continue
            chap_id = 1 + len(self.chapters)
            self.chapters.append({
                "id": chap_id,
                "title": a.text.strip(),
                "url": self.absolute_url(a['href']).strip('/') + '/',
            })

        # NOTE: JSON files are not available now
        # for item in soup.select("div.ch-list amp-list"):
        #     data = self.get_json(item["src"])
        #     for chapter in data["items"]:
        #         chap_id = 1 + len(self.chapters)
        #         vol_id = 1 + len(self.chapters) // 100
        #         if len(self.chapters) % 100 == 0:
        #             self.volumes.append({"id": vol_id})
        #         self.chapters.append(
        #             {
        #                 "id": chap_id,
        #                 "volume": vol_id,
        #                 "url": chapter["permalink"],
        #                 "title": chapter["no"] + " " + chapter["title"],
        #             }
        #         )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)
        contents = soup.select_one(".post .post-content .par")
        return self.cleaner.extract_contents(contents)
