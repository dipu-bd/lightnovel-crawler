import logging
import re
from typing import Iterable, Mapping, Optional
from urllib.parse import urlencode

from lncrawl.context import ctx
from lncrawl.core import BrowserTemplate, Chapter, Crawler, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)


_automation_warning = """
<div style="opacity: 0.5; padding: 14px; text-align: center; border: 1px solid #000; font-style: italic; font-size: 0.825rem">
    Parsed with an automated reader. The content accuracy is not guaranteed.
</div>
""".strip()

_title_matcher = re.compile(r"^(c|ch|chap|chapter)?[^\w\d]*(\d+)$", flags=re.I)


class NovelupdatesCrawler(BrowserTemplate):
    base_url = ["https://www.novelupdates.com/"]

    _cached_crawlers: Mapping[str, Crawler] = {}
    search_item_list_selector = ".l-main .search_main_box_nu"
    search_item_title_selector = ".search_title a[href]"
    search_item_url_selector = ".search_title a[href]"
    search_item_info_selector = ".genre_rank"
    search_item_rating_selector = ".search_ratings"
    search_item_chapter_count_selector = '.ss_desk i[title="Chapter Count"]'
    search_item_last_updated_selector = '.ss_desk i[title="Last Updated"]'
    search_item_reviewers_selector = '.ss_desk i[title="Reviews"]'

    novel_title_selector = ".seriestitlenu"
    novel_cover_selector = ".seriesimg img[src]"
    novel_author_selector = "#showauthors a#authtag"
    novel_synopsis_selector = "#editdescription"
    novel_tags_selector = "#showtags a.genre"

    def initialize(self):
        self.taskman.init_executor(workers=4)

    # def wait_for_cloudflare(self):
    #     if "cf_clearance" in self.scraper.cookies:
    #         return
    #     try:
    #         self.browser.wait(
    #             "#challenge-running",
    #             expected_conditon=EC.invisibility_of_element,
    #             timeout=20,
    #         )
    #     except Exception:
    #         pass

    def cleanup_prompts(self):
        try:
            elem = self.browser.find("#uniccmp")
            if elem:
                elem.remove()
        except Exception:
            pass

    def build_search_url(self, query: str) -> str:
        params = dict(
            sf=1,
            sh=query,
            sort="srank",
            order="asc",
            rl=1,
            mrl="min",
        )
        return f"https://www.novelupdates.com/series-finder/?{urlencode(params)}"

    def parse_search_item_info(self, soup: PageSoup) -> str:
        info = []
        rank = soup.select_one(self.search_item_info_selector)
        rating = soup.select_one(self.search_item_rating_selector)
        chapter_count = soup.select_one(self.search_item_chapter_count_selector)
        last_updated = soup.select_one(self.search_item_last_updated_selector)
        reviewers = soup.select_one(self.search_item_reviewers_selector)
        if rating:
            info.append(rating.text.strip())
        if rank:
            info.append("Rank " + rank.text.strip())
        if reviewers:
            info.append(reviewers.parent.text.strip())
        if chapter_count:
            info.append(chapter_count.parent.text.strip())
        if last_updated:
            info.append(last_updated.parent.text.strip())
        return " | ".join(info)

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        postid = soup.select_one("input#mypostid")["value"]
        response = self.scraper.submit_form(
            f"{self.scraper.origin}wp-admin/admin-ajax.php",
            data=dict(
                action="nd_getchapters",
                mygrr="1",
                mypostid=postid,
            ),
        )
        soup = self.scraper.make_soup(response)
        return reversed(soup.select(".sp_li_chp a[data-id]"))

    # def select_chapter_tags_in_browser(self):
    #     self.cleanup_prompts()
    #     el = self.browser.find(".my_popupreading_open")
    #     el.scroll_into_view()
    #     el.click()

    #     self.browser.wait("#my_popupreading li.sp_li_chp a[data-id]")
    #     tag = self.browser.find("#my_popupreading").as_tag()
    #     yield from reversed(tag.select("li.sp_li_chp a[data-id]"))

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        title = soup.text.strip().title()
        title_match = _title_matcher.match(title)
        if title_match:  # skip simple titles
            title = f"Chapter {title_match.group(2)}"
        return Chapter(
            title=title,
            id=chapter_id,
            url=self.absolute_url(soup["href"]),
        )

    def download_chapter(self, chapter: Chapter) -> None:
        response = self.scraper.get(chapter.url)
        chapter.url = response.url
        try:
            constructor = ctx.sources.get_crawler(chapter.url)
            crawler = ctx.sources.init_crawler(constructor)
            crawler.scraper.signal = self.scraper.signal
            crawler.download_chapter(chapter)
        except Exception:
            logger.info("Failed to download chapter using original crawler.", exc_info=True)
            from readability import Document  # type: ignore

            reader = Document(response.text)
            chapter.title = reader.short_title()
            summary = reader.summary(html_partial=True)
            return _automation_warning + summary

    # def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
    #     self.visit(chapter.url)
    #     for i in range(30):
    #         if not self.browser.current_url.startswith(chapter.url):
    #             break
    #         time.sleep(1)

    #     logger.info("%s => %s", chapter.url, self.browser.current_url)
    #     chapter.url = self.browser.current_url
    #     return self.parse_chapter_body(chapter, self.browser.html)
