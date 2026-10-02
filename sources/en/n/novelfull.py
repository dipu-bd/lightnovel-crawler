# -*- coding: utf-8 -*-
import logging
from typing import Iterable, Optional
from urllib.parse import urlencode

from lncrawl.core import Novel, PageSoup, Volume
from lncrawl.exceptions import LNException
from lncrawl.templates.novelfull import NovelFullTemplate

logger = logging.getLogger(__name__)


class NovelFullCrawler(NovelFullTemplate):
    base_url = [
        "http://novelfull.com/",
        "https://novelfull.com/",
        "https://novelfull.net/",
    ]

    chapter_list_batch_size = 5

    def _fetch_chapter_page(
        self,
        list_url: str,
        novel_id: str,
        page: int,
    ) -> tuple[list[PageSoup], int, int]:
        query = urlencode(
            {
                "novelId": novel_id,
                "page": page,
            }
        )
        separator = "&" if "?" in list_url else "?"
        url = self.absolute_url(f"{list_url}{separator}{query}")

        response = self.scraper.get(url)
        data = response.json()

        if not isinstance(data, dict):
            raise LNException(f"Invalid chapter list result for page {page}")

        code = data.get("code")
        if code not in (None, 200, "200"):
            raise LNException(f"Chapter list request failed for page {page}: code={code}")

        returned_page = data.get("page")
        if returned_page is not None and int(returned_page) != page:
            raise LNException(
                f"Unexpected chapter list page: requested {page}, got {returned_page}"
            )

        html = data.get("html")
        if not isinstance(html, str) or not html.strip():
            raise LNException(f"Empty chapter list result for page {page}")

        soup = self.scraper.make_soup(html)

        chapter_tags = soup.select("li > a.con[href]")
        if not chapter_tags:
            chapter_tags = soup.select("li > a[href]")

        if not chapter_tags:
            raise LNException(f"No chapters found on chapter list page {page}")

        total_pages = int(data.get("totalPage") or 0)
        total_chapters = int(data.get("totalChapters") or 0)

        return chapter_tags, total_pages, total_chapters

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        list_tag = tag.select_one("#list-chapter[data-novel-id][data-list-url]")
        if not list_tag:
            return super().select_chapter_tags(tag, novel, volume)

        novel_id = list_tag.get_attr("data-novel-id")
        list_url = list_tag.get_attr("data-list-url")
        if not novel_id or not list_url:
            return super().select_chapter_tags(tag, novel, volume)

        html_total_pages = int(list_tag.get_attr("data-total-page") or 0)
        html_total_chapters = int(list_tag.get_attr("data-total-chapters") or 0)

        first_page, ajax_total_pages, ajax_total_chapters = self._fetch_chapter_page(
            list_url,
            novel_id,
            1,
        )

        chapter_tags = list(first_page)
        total_pages = ajax_total_pages or html_total_pages or 1
        expected_total = ajax_total_chapters or html_total_chapters

        page = 2
        while page <= total_pages:
            batch_end = min(
                page + self.chapter_list_batch_size - 1,
                total_pages,
            )
            futures = [
                self.taskman.submit_task(
                    self._fetch_chapter_page,
                    list_url,
                    novel_id,
                    current_page,
                )
                for current_page in range(page, batch_end + 1)
            ]

            try:
                for future in futures:
                    (
                        page_chapters,
                        fresh_total_pages,
                        fresh_total_chapters,
                    ) = future.result()

                    chapter_tags.extend(page_chapters)

                    if fresh_total_pages:
                        total_pages = max(total_pages, fresh_total_pages)
                    if fresh_total_chapters:
                        expected_total = max(
                            expected_total,
                            fresh_total_chapters,
                        )
            except Exception:
                self.taskman.cancel_futures(futures)
                raise

            page = batch_end + 1

        if expected_total and len(chapter_tags) != expected_total:
            raise LNException(
                f"Incomplete chapter list: expected {expected_total}, got {len(chapter_tags)}"
            )

        return chapter_tags

    def initialize(self) -> None:
        self.cleaner.bad_css.update(
            [
                'div[align="left"]',
                'img[src*="proxy?container=focus"]',
            ]
        )
