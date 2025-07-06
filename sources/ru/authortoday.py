# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

headers = {
    "Authorization": "Bearer guest",
    "Cookie": "AdultUser=true",
}


class AuthorTodayCrawler(Crawler):
    base_url = ["https://author.today/"]

    def initialize(self):
        self.init_executor(workers=1)

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        book_info = self.get_json(
            f"https://api.author.today/v1/work/{self.novel_url.split('/')[-1]}/details",
            headers=headers,
        )

        self.novel_title = book_info["title"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = book_info["coverUrl"]
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_synopsis = (
            book_info["annotation"] if book_info["annotation"] else None
        )
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        chap_id = 0
        for chapter in book_info["chapters"]:
            if not chapter["isAvailable"]:
                continue

            chap_id = chap_id + 1
            self.chapters.append(
                {
                    "id": chap_id,
                    "url": f"https://author.today/reader/{chapter['workId']}/chapter?id={chapter['id']}",
                    "title": chapter["title"],
                }
            )

    def download_chapter_body(self, chapter):
        response = self.get_response(chapter["url"])
        chapter_data = response.json()["data"]["text"]
        reader_secret = response.headers["Reader-Secret"]
        cipher = "".join(reversed(reader_secret)) + "@_@"

        # encode and remove header
        dirt_chapter = list(chapter_data.encode("utf-16"))[2:]
        # concatenate two adjacent bytes
        chapter_e_bytes = [
            (b << 8) | a for a, b in zip(dirt_chapter[0::2], dirt_chapter[1::2])
        ]

        # utf-16 header
        chapter_d_bytes = [65279]

        for i in range(0, len(chapter_e_bytes)):
            chapter_d_bytes.append(chapter_e_bytes[i] ^ ord(cipher[i % len(cipher)]))

        # split by bytes, concatenate sequences and decode
        chapter_content = bytes(
            [b for a in chapter_d_bytes for b in [a >> 8, a & 0xFF]]
        ).decode("utf-16")

        return chapter_content
