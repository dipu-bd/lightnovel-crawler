# -*- coding: utf-8 -*-
import logging
import operator
from urllib.parse import urlencode

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RanobeLibMeCrawler(Crawler):
    base_url = [
        "https://ranobelib.me/",
    ]

    def initialize(self):
        self.init_executor(ratelimit=0.99)
        clean_url = self.novel_url.split("?")[0].strip("/")
        self.api_url = f"https://api.cdnlibs.org/api/manga/{clean_url.split('/')[-1]}"

    def read_novel_info(self):
        api_requests_params = {
            "fields[]": [
                "background",
                "eng_name",
                "otherNames",
                "summary",
                "genres",
                "chap_count",
                "status_id",
                "authors",
                "format",
            ]
        }

        logger.debug("Visiting %s", self.novel_url)
        book_info = self.get_json(
            f"{self.api_url}?{urlencode(api_requests_params, doseq=True)}"
        )

        self.novel_title = book_info["data"]["rus_name"]
        logger.info("Novel title: %s", self.novel_title)

        novel_cover = book_info["data"]["cover"]["default"]
        if "https" not in novel_cover:
            novel_cover = f"https://ranobelib.me/{novel_cover}"
        self.novel_cover = novel_cover
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = book_info["data"]["authors"][0]["name"]
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = book_info["data"]["summary"]
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        genres = book_info["data"]["genres"]
        self.novel_tags = [item["name"] for item in genres]
        logger.info("Novel tags: %s", self.novel_tags)

        chapters = self.get_json(f"{self.api_url}/chapters")["data"]
        chap_id = 0

        branches = dict()
        for chapter in chapters:
            for branch in chapter["branches"]:
                key = branch["branch_id"]
            branches[key] = branches.setdefault(key, 0) + 1
        branch = max(branches.items(), key=operator.itemgetter(1))[0]
        if not isinstance(branch, int):
            branch = 0

        for chapter in chapters:
            if any(
                "moderation" in chapter_branch for chapter_branch in chapter["branches"]
            ):
                continue

            """ Left it temporarily, to be fixed later """
            # if not any(
            #     chapter_branch["branch_id"] == branch
            #     for chapter_branch in chapter["branches"]
            # ):
            #     continue

            chap_id = chap_id + 1
            chap_num = chapter["number"]

            params = {
                "volume": chapter["volume"],
                "number": chapter["number"],
                "branch_id": branch,
            }

            self.chapters.append(
                {
                    "id": chap_id,
                    "url": f"{self.api_url}/chapter?{urlencode(params, doseq=True)}",
                    "title": chapter["name"] or (f"Глава {chap_num}"),
                }
            )

    def download_chapter_body(self, chapter):
        chapter = self.get_json(chapter["url"])

        if "content" in chapter["data"]["content"]:
            paragraphs = self._paragraph_parser(data=chapter["data"])
            chapter_content = "".join(
                [
                    f"<p>{text['text']}</p>"
                    for tag in paragraphs
                    for text in tag
                    if "text" in text
                ]
            )
            return chapter_content

        else:
            chapter_content = self.make_soup(chapter["data"]["content"])
            return self.cleaner.extract_contents(chapter_content)

    def _paragraph_parser(self, data):
        paragraphs = []

        if isinstance(data, dict):
            for key, value in data.items():
                if key == "type" and value == "paragraph":
                    paragraphs.append(data.get("content", ""))
                else:
                    paragraphs.extend(self._paragraph_parser(value))

        elif isinstance(data, list):
            for item in data:
                paragraphs.extend(self._paragraph_parser(item))

        return paragraphs
