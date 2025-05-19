# -*- coding: utf-8 -*-
import json
import logging
import re

from box import Box
from bs4 import BeautifulSoup

from lncrawl.core.crawler import Chapter, Crawler, Volume
from lncrawl.core.exeptions import LNException

logger = logging.getLogger(__name__)


class ChereadsCrawler(Crawler):
    base_url = ["https://www.chereads.com/"]

    def initialize(self):
        self.init_executor(workers=5)

    def parse_metadata(self, soup: BeautifulSoup) -> Box:
        metadata_json = soup.select_one("script#__NEXT_DATA__, script#vite-plugin-ssr_pageContext")
        if not metadata_json:
            raise LNException('No metadata')
        script_text = metadata_json.text
        json_data = json.loads(script_text)
        return Box(json_data)

    def read_novel_info(self) -> None:
        if '/chapterlist/' in self.novel_url:
            novel_id = self.novel_url.split('/chapterlist/', 2)[1]
            self.novel_url = f'https://www.chereads.com/novel/{novel_id}'
        soup = self.get_soup(self.novel_url.strip("/"))
        metadata = self.parse_metadata(soup)

        book_info = metadata.props.pageProps.data.bookInfo

        book_id = str(book_info.bookId)
        cover_base_url = 'https://book-pic.webnovel.com/1001/bookcover/'
        self.novel_cover = f'{cover_base_url}{book_id}'

        self.novel_title = str(book_info.bookName)
        self.novel_author = str(book_info.authorName)
        self.novel_synopsis = str(book_info.description)
        self.novel_tags = [item.tagName for item in book_info.tagInfos]

        for vol in metadata.props.pageProps.data.volumeItems:
            vol_id = len(self.volumes) + 1
            self.volumes.append(
                Volume(
                    id=vol_id,
                    title=vol.volumeName,
                )
            )
            for chap in vol.chapterItems:
                if chap.isAuth == 0:
                    continue
                self.chapters.append(
                    Chapter(
                        volume=vol_id,
                        id=len(self.chapters) + 1,
                        title=f'#{chap.chapterIndex} {chap.chapterName}',
                        url=f"{self.novel_url.strip('/')}/{chap.chapterId}",
                    )
                )

    def download_chapter_body(self, chapter: Chapter) -> str:
        soup = self.get_soup(chapter.url)
        metadata = self.parse_metadata(soup)
        contents = metadata.pageProps.pageData.chapterInfo.contents

        paras = [str(item.content) for item in contents]
        if re.match(r'<p>[Cc]h(ap(ter)?)?.\d+', paras[0]):
            chapter.title = paras[0][3:-4]
            paras = paras[1:]

        return "".join(paras)
