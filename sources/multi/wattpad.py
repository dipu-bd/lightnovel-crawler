# -*- coding: utf-8 -*-
from time import time
import logging
import re
from urllib.parse import urlparse
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_info_url = (
    "https://www.wattpad.com/v4/parts/%s?fields=id,title,pages,text_url&_=%d"
)
story_info_url = "https://www.wattpad.com/api/v3/stories/%s"


class WattpadCrawler(Crawler):
    base_url = [
        "https://www.wattpad.com/",
        "https://my.w.tt/",
    ]

    def initialize(self):
        self.home_url = "https://www.wattpad.com/"

    def login(self, email: str, password: str) -> None:
        resp = self.submit_form(
            "https://www.wattpad.com/login?nextUrl=/home",
            data={
                "username": email,
                "password": password,
            },
        )
        apiAuthKey = re.findall(r"wattpad\.apiAuthKey = '([^']+)';", resp.text)
        if not apiAuthKey:
            raise Exception("Failed to login")
        logger.info("authorization", apiAuthKey[0])
        self.set_header("authorization", apiAuthKey[0])

        data = self.get_json(
            "https://www.wattpad.com/api/v3/internal/current_user?fields=email,username,name"
        )
        logger.debug("current user", data)
        if email.lower() != data["username"].lower():
            raise Exception("Failed to login")
        print(
            "Logged in as %s[%s]<%s>" % (data["name"], data["username"], data["email"])
        )

    def read_novel_info(self):

        search_id = re.compile(r"\d+")
        id_no = search_id.search(self.novel_url)
        story_url = story_info_url % (id_no.group())

        logger.debug("Visiting %s", story_url)
        story_info = self.get_json(story_url)

        self.novel_title = story_info["title"]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(story_info["cover"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = story_info["user"]["name"]
        logger.info("Novel author: %s", self.novel_author)

        chapters = story_info["parts"]

        for a in chapters:
            self.chapters.append(
                {
                    "id": len(self.chapters) + 1,
                    "url": self.absolute_url(a["url"]),
                    "title": a["title"],
                }
            )

    def download_chapter_body(self, chapter):
        chapter_id = urlparse(chapter["url"]).path.split("-")[0].strip("/")
        info_url = chapter_info_url % (chapter_id, int(time() * 1000))

        logger.info("Getting info %s", info_url)
        data = self.get_json(info_url)
        chapter["title"] = data["title"]

        text_url = data["text_url"]["text"]
        logger.info("Getting text %s", text_url)
        text = self.get_response(text_url).content.decode("utf8")
        text = re.sub(r'<p data-p-id="[a-f0-9]+>"', "<p>", text)
        return text
