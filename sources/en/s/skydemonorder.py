import logging
import json
from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)


class SkyDemonOrder(Crawler):
    base_url = "https://skydemonorder.com"

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1").text.strip()
        assert possible_title, "No novel title"
        self.novel_title = possible_title
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("img[alt='{self.novel_title}']")
        if possible_image:
            self.novel_cover = possible_image["src"]
        logger.info("Novel cover: %s", self.novel_cover)

        section = soup.find_all("section", attrs={"x-data": True})

        if len(section) == 1:
            chapter_section = section[0]
        else:
            chapter_section = section[1]

        section_data = "".join(chapter_section.get("x-data").split("})(")[1].split())[
            :-2
        ]  # remove all whitespace & remove last 2 chars

        chapters_obj = json.loads(section_data)

        if isinstance(chapters_obj, list) is False:
            chapters = []
            for _, value in chapters_obj.items():
                chapters.append(value)

        else:
            chapters = chapters_obj

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
                    "url": self._make_url(item["slug"], item["project"]["slug"]),
                    "title": item["full_title"],
                }
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".prose")

        return self.cleaner.extract_contents(contents)

    def _make_url(self, slug, project_slug):
        return self.absolute_url("/" + "projects" + "/" + project_slug + "/" + slug)
