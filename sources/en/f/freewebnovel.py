import re
from typing import Iterable, Optional
from urllib.parse import urlencode

from scraper import PageSoup

from lncrawl.core.models import Chapter, Novel, Volume
from lncrawl.templates.freewebnovel import FreewebnovelTemplate


class FreewebnovelCrawler(FreewebnovelTemplate):
    base_url = [
        "https://freewebnovel.com/",
    ]

    def _get_chapter_pagination(self, tag: PageSoup) -> tuple[int, int]:
        """Extract totalPage and pageSize from window.chapterPagination script."""
        for script in tag.select("script"):
            text = script.get_text()
            if "chapterPagination" not in text:
                continue
            total_page_m = re.search(r"totalPage\s*:\s*(\d+)", text)
            page_size_m = re.search(r"pageSize\s*:\s*(\d+)", text)
            if total_page_m:
                total_page = int(total_page_m.group(1))
                page_size = int(page_size_m.group(1)) if page_size_m else 40
                return total_page, page_size
        # fallback: count static options if server-rendered
        option_count = len(tag.select(".page #indexselect option"))
        return max(option_count, 1), 40

    def select_chapter_tags(
        self,
        tag: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        clean_url = novel.url.split("?")[0]
        total_page, page_size = self._get_chapter_pagination(tag)
        futures = [
            self.taskman.submit_task(
                self.scraper.submit_form,
                url=clean_url
                + "?"
                + urlencode(
                    {
                        "ajax": "chapters",
                        "page": page,
                        "pageSize": page_size,
                    }
                ),
            )
            for page in range(1, total_page + 1)
        ]
        for resp in self.taskman.resolve(
            futures,
            desc="Index",
            unit="page",
            fail_fast=True,
        ):
            assert resp, "failed to fetch chapter list"
            data = resp.json()
            assert "html" in data, "invalid chapter list result"
            soup = self.scraper.make_soup(data["html"])
            yield from soup.select("a[href]")

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        chapter = Chapter(id=chapter_id)
        chapter.title = soup.get_attr("title")
        chapter.url = self.absolute_url(soup.get_attr("href"))
        return chapter
