# -*- coding: utf-8 -*-
import json
import logging

from box import Box
from lncrawl.core.crawler import Crawler, Volume, Chapter

logger = logging.getLogger(__name__)


class ChereadsCrawler(Crawler):
    base_url = ["https://www.chereads.com/"]

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url.strip("/"))

        metadata_json = soup.select_one("script#__NEXT_DATA__")
        metadata = Box(json.loads(metadata_json.text))

        book_info = metadata.props.pageProps.data.bookInfo
        book_id = book_info["bookId"]

        self.novel_title = book_info["bookName"]
        self.novel_author = book_info["authorName"]
        self.novel_cover = f"https://book-pic.webnovel.com/1001/bookcover/{book_id}"
        self.novel_synopsis = book_info["description"]
        self.novel_tags = [item["tagName"] for item in book_info["tagInfos"]]

        for vol in metadata.props.pageProps.data.volumeItems:
            self.volumes.append(
                Volume(
                    id=vol["volumeId"],
                    title=vol["volumeName"],
                )
            )
            for chap in vol["chapterItems"]:
                if chap["isAuth"] == 0:
                    continue
                self.chapters.append(
                    Chapter(
                        id=chap["chapterIndex"],
                        volume=vol["volumeId"],
                        url=f"{self.novel_url}{chap['chapterId']}",
                        title=f'#{chap["chapterIndex"]} {chap["chapterName"]}',
                    )
                )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)

        metadata_json = soup.select_one("script#vite-plugin-ssr_pageContext")
        metadata = Box(json.loads(metadata_json.text))

        contents = metadata.pageProps.pageData.chapterInfo.contents
        return "".join([item["content"] for item in contents])
