# -*- coding: utf-8 -*-
import logging
from urllib.parse import urlencode

from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter

logger = logging.getLogger(__name__)


class RaeiTranslationsCrawler(Crawler):
    base_url = ["https://raeitranslations.com/"]
    novel_json_url_prefix = "https://api.raeitranslations.com/api/novels/"
    novel_cover_url_prefix = "https://raeitranslations.com/assets/"
    novel_chapters_list_url_prefix = "https://api.raeitranslations.com/api/chapters/list?"
    novel_chapter_url_prefix = "https://api.raeitranslations.com/api/chapters/single?"
    json_request_headers = {
        "Accept": "*/*"
    }

    def read_novel_info(self) -> None:
        title = self.novel_url.rstrip("/").split("/")[-1]
        novel_json = self.get_json(
            f"{self.novel_json_url_prefix}{title}",
            headers=self.json_request_headers
        )
        self.novel_title = novel_json["novTitle"]
        self.novel_author = novel_json["novAuthor"]
        self.novel_synopsis = novel_json["sum"]
        self.novel_cover = f"{self.novel_cover_url_prefix}{title}.jpg"

        params_chapters = {"novTitleId": title}
        chapters_json = self.get_json(
            f"{self.novel_chapters_list_url_prefix}{urlencode(params_chapters)}",
            headers=self.json_request_headers
        )

        for index, json in enumerate(chapters_json):
            params = {"id": title, "num": json["chapIndex"]}
            self.chapters.append(
                Chapter(
                    id=index,
                    title=f"{json['tagPrefix']}{json['chapTag']} {json['chapTitle']}",
                    url=f"{self.novel_chapter_url_prefix}{urlencode(params)}"
                )
            )

    def download_chapter_body(self, chapter: Chapter) -> str:
        json = self.get_json(chapter.url, headers=self.json_request_headers)
        content = str(json["currentChapter"]["body"])
        soup = self.make_soup(content.replace('\n', '<br>'))
        return self.cleaner.extract_contents(soup)
