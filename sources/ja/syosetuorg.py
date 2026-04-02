# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)
search_url = "https://syosetu.org/search/?mode=search&word=%s"


class SyosetuOrgCrawler(BrowserTemplate):
    base_url = "https://syosetu.org/"

    search_item_list_selector = ".searchkekka_box"
    search_item_title_selector = ".novel_h a"
    search_item_url_selector = ".novel_h a"

    novel_title_selector = "#maind span[itemprop='name']"
    novel_author_selector = "#maindspan[itemprop='author'] a"
    novel_tags_selector = '#maind span[itemprop="genre"] a'
    novel_synopsis_selector = "#maind .ss:nth-of-type(2)"

    novel_chapter_body_selector = "#honbun"

    def initialize(self) -> None:
        self.taskman.init_executor(workers=2)

    def build_search_url(self, query: str) -> str:
        return search_url % quote_plus(query)

    def search_novel_item_info(self, soup: PageSoup) -> str:
        votes = soup.select_one(".attention").text
        latest = soup.select_one(".left").get_text(" ", True)
        return f"{latest} | {votes}"

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        title_tag = soup.select_one(self.novel_title_selector)
        if not title_tag:
            novel.title = soup.select_one("title").text.split(" - ")[0]
        novel.title = title_tag.text

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        volume_id = 0
        for tr in soup.select("#maind table tr"):
            print(tr)
            tds = tr.select("td")
            if len(tds) == 1 and tds[0].get("colspan") == "2":
                # volume header
                strong = tds[0].select_one("strong")
                if not strong:
                    continue

                volume_id = len(novel.volumes) + 1
                novel.volumes.append(Volume(id=volume_id, title=strong.text))

            elif len(tds) == 2:
                # chapter row
                a = tds[0].select_one("a[href]")
                if not a:
                    continue

                chapter_id = len(novel.chapters) + 1
                if volume_id == 0:
                    volume_id = 1
                    novel.volumes.append(Volume(id=volume_id))

                novel.chapters.append(
                    Chapter(
                        id=chapter_id,
                        volume=volume_id,
                        title=a.text,
                        url=self.absolute_url(a["href"]),
                    )
                )

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.scraper.get_soup(chapter.url)
        contents = soup.select_one(self.novel_chapter_body_selector)
        self.cleaner.clean_contents(contents)
        chapter.body = "".join([str(p) for p in contents.select("p") if p])
        if not chapter.body:
            chapter.body = str(contents)
