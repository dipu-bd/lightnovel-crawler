# -*- coding: utf-8 -*-
import logging
import re
from urllib.parse import urlsplit

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class ZenkoCrawler(LegacyCrawler):
    base_url = ["https://zenko.online/"]
    language = "uk"
    request_rate_limit = 1
    api_url = "https://api.zenko.online"

    def read_novel_info(self):
        path_parts = [part for part in urlsplit(self.novel_url).path.split("/") if part]
        if len(path_parts) < 2 or path_parts[0] != "titles":
            raise ValueError(f"Invalid Zenko title URL: {self.novel_url}")

        title_id = path_parts[1]
        title = self.get_json(f"{self.api_url}/titles/{title_id}")
        if title.get("category") != "RANOBE":
            # Only RANOBE titles hold text: every other category returns image
            # file ids in `pages[].content`, which would land in the epub as-is.
            raise ValueError(
                f"Not a text novel (category={title.get('category')}): {self.novel_url}"
            )

        self.novel_title = title["name"]
        self.novel_author = ", ".join(writer["name"] for writer in title.get("writers", []))
        self.novel_synopsis = title.get("description") or ""
        self.novel_tags = [tag["name"] for tag in title.get("genres", [])]
        self.novel_cover = f"https://storage.zenko.online/{title['coverImg']}"

        chapter_items = self.get_json(f"{self.api_url}/titles/{title_id}/chapters")
        volume = Volume(id=1, title="")
        self.volumes.append(volume)
        for index, item in enumerate(chapter_items, start=1):
            if not item.get("isPublished"):
                continue
            name = re.search(r"(\d+)$", item.get("name", ""))
            chapter_number = name.group(1) if name else str(index)
            self.chapters.append(
                Chapter(
                    volume=volume.id,
                    id=len(self.chapters) + 1,
                    title=f"Chapter {chapter_number}",
                    url=f"{self.api_url}/chapters/{item['id']}",
                )
            )

    def download_chapter_body(self, chapter):
        data = self.get_json(chapter.url)
        pages = sorted(data.get("pages", []), key=lambda page: page.get("order", 0))
        return "".join(page.get("content", "") for page in pages)
