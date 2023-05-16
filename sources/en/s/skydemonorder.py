import logging

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)


class SkyDemonOrder(Crawler):
    base_url = "https://skydemonorder.com"

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(f"h1").text.strip()
        assert possible_title, "No novel title"
        self.novel_title = possible_title
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("img[alt='{self.novel_title}']")
        if possible_image:
            self.novel_cover = possible_image["src"]
        logger.info("Novel cover: %s", self.novel_cover)

        chapters = soup.select(
            'section[x-data="{ expanded: 1 }"] div.text-sm div.flex a'
        )
        chapters.reverse()

        for item in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100

            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})

            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(item["href"]),
                    "title": item.text,
                }
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".prose")

        return self.cleaner.extract_contents(contents)
