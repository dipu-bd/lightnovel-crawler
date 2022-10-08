import logging
import re

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


# Created using AsianHobbyist as a template.
class AsianNovelCrawler(Crawler):
    base_url = "https://read.asianovel.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        novel_toc_url = self.novel_url + "/table-of-contents"
        soup = self.get_soup(novel_toc_url)

        possible_title = soup.select_one(".novel-description-full")
        assert possible_title, "No novel title"

        self.novel_title = possible_title.get_text()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("article:first-of-type .row img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        self.volumes.append({"id": 1})
        for a in soup.select("#toc > div a"):
            title = a.select_one("div:first-of-type").get_text().strip()

            chap_id = len(self.chapters) + 1
            match = re.findall(r"ch(apter)? (\d+)", title, re.IGNORECASE)
            if len(match) == 1:
                chap_id = int(match[0][1])

            self.chapters.append(
                {
                    "volume": 1,
                    "id": chap_id,
                    "title": title,
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        logger.debug("Visiting %s", chapter["url"])
        soup = self.get_soup(chapter["url"])

        content = soup.select_one("#story")
        self.cleaner.clean_contents(content)

        return "".join([str(p) for p in content.select("p") if len(p.text.strip()) > 1])
