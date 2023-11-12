import logging
import re
import time
from typing import Mapping
from urllib.parse import urlencode, urlparse

from bs4 import BeautifulSoup, Tag
from readability import Document

from lncrawl.core.browser import EC
from lncrawl.core.crawler import Crawler
from lncrawl.models import Chapter, SearchResult
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate
from lncrawl.templates.browser.searchable import SearchableBrowserTemplate

logger = logging.getLogger(__name__)


automation_warning = """
<div style="opacity: 0.5; padding: 14px; text-align: center; border: 1px solid #000; font-style: italic; font-size: 0.825rem">
    Parsed with an automated reader. The content accuracy is not guaranteed.
</div>
""".strip()


class NovelupdatesTemplate(SearchableBrowserTemplate, ChapterOnlyBrowserTemplate):
    is_template = True
    _cached_crawlers: Mapping[str, Crawler] = {}
    _title_matcher = re.compile(r"^(c|ch|chap|chapter)?[^\w\d]*(\d+)$", flags=re.I)

    def initialize(self):
        self.init_executor(
            workers=4,
        )

    def wait_for_cloudflare(self):
        if "cf_clearance" in self.cookies:
            return
        try:
            self.browser.wait(
                "#challenge-running",
                expected_conditon=EC.invisibility_of_element,
                timeout=20,
            )
        except Exception:
            pass

    def cleanup_prompts(self):
        try:
            self.browser.find("#uniccmp").remove()
        except Exception:
            pass

    def select_search_items(self, query: str):
        query = dict(sf=1, sh=query, sort="srank", order="asc", rl=1, mrl="min")
        soup = self.get_soup(
            f"https://www.novelupdates.com/series-finder/?{urlencode(query)}"
        )
        yield from soup.select(".l-main .search_main_box_nu")

    def select_search_items_in_browser(self, query: str):
        query = dict(sf=1, sh=query, sort="srank", order="asc", rl=1, mrl="min")
        self.visit(f"https://www.novelupdates.com/series-finder/?{urlencode(query)}")
        self.browser.wait(".l-main .search_main_box_nu")
        yield from self.browser.soup.select(".l-main .search_main_box_nu")

    def parse_search_item(self, tag: Tag) -> SearchResult:
        a = tag.select_one(".search_title a[href]")

        info = []
        rank = tag.select_one(".genre_rank")
        rating = tag.select_one(".search_ratings")
        chapter_count = tag.select_one('.ss_desk i[title="Chapter Count"]')
        last_updated = tag.select_one('.ss_desk i[title="Last Updated"]')
        reviewers = tag.select_one('.ss_desk i[title="Reviews"]')
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

        return SearchResult(
            title=a.text.strip(),
            info=" | ".join(info),
            url=self.absolute_url(a["href"]),
        )

    def parse_title(self, soup: BeautifulSoup) -> str:
        return soup.select_one(".seriestitlenu").text

    def parse_title_in_browser(self) -> str:
        self.browser.wait(".seriestitlenu")
        return self.parse_title(self.browser.soup)

    def parse_cover(self, soup: BeautifulSoup) -> str:
        img_tag = soup.select_one(".seriesimg img[src]")
        if img_tag:
            return img_tag["src"]

    def parse_authors(self, soup: BeautifulSoup):
        for a in soup.select("#showauthors a#authtag"):
            yield a.text.strip()

    def select_chapter_tags(self, soup: BeautifulSoup):
        postid = soup.select_one("input#mypostid")["value"]
        response = self.submit_form(
            "https://www.novelupdates.com/wp-admin/admin-ajax.php",
            data=dict(
                action="nd_getchapters",
                mygrr="1",
                mypostid=postid,
            ),
        )
        soup = self.make_soup(response)
        yield from reversed(soup.select(".sp_li_chp a[data-id]"))

    def select_chapter_tags_in_browser(self):
        self.cleanup_prompts()
        el = self.browser.find(".my_popupreading_open")
        el.scroll_into_view()
        el.click()

        self.browser.wait("#my_popupreading li.sp_li_chp a[data-id]")
        tag = self.browser.find("#my_popupreading").as_tag()
        yield from reversed(tag.select("li.sp_li_chp a[data-id]"))

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        title = tag.text.strip().title()
        title_match = self._title_matcher.match(title)
        if title_match:  # skip simple titles
            title = f"Chapter {title_match.group(2)}"
        return Chapter(
            id=id,
            title=title,
            url=self.absolute_url(tag["href"]),
        )

    def download_chapter_body_in_scraper(self, chapter: Chapter) -> None:
        response = self.get_response(chapter.url, allow_redirects=True)
        logger.info("%s => %s", chapter.url, response.url)
        chapter.url = response.url
        return self.parse_chapter_body(chapter, response.text)

    def download_chapter_body_in_browser(self, chapter: Chapter) -> str:
        self.visit(chapter.url)
        for i in range(30):
            if not self.browser.current_url.startswith(chapter.url):
                break
            time.sleep(1)

        logger.info("%s => %s", chapter.url, self.browser.current_url)
        chapter.url = self.browser.current_url
        return self.parse_chapter_body(chapter, self.browser.html)

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        return super().select_chapter_body(soup)

    def parse_chapter_body(self, chapter: Chapter, text: str) -> str:
        if "re-library" in chapter.url and "translations" not in chapter.url:
            soup = self.get_soup(chapter.url)
            post_url = soup.select_one(".entry-content > p[style*='center'] a")['href']
            if "page_id" in post_url:
                chapter.url = post_url
            else:
                time.sleep(2.5)
                novel_url = f"https://re-library.com/translations/{post_url.split('/')[4:5][0]}"
                response = self.get_soup(novel_url)
                chapters = response.select(".page_item > a")
                chapter.url = chapters[chapter.id - 1]["href"]
                time.sleep(2.5)

        crawler = self._find_original_crawler(chapter)
        if hasattr(crawler, "download_chapter_body_in_scraper"):
            return crawler.download_chapter_body_in_scraper(chapter)
        elif hasattr(crawler, "download_chapter_body"):
            return crawler.download_chapter_body(chapter)
        else:
            reader = Document(text)
            chapter.title = reader.short_title()
            summary = reader.summary(html_partial=True)
            return automation_warning + summary

    def _find_original_crawler(self, chapter: Chapter):
        from lncrawl.core.sources import crawler_list, prepare_crawler

        parsed_url = urlparse(chapter.url)
        base_url = "%s://%s/" % (parsed_url.scheme, parsed_url.hostname)

        if base_url in crawler_list:
            try:
                crawler = self._cached_crawlers.get(base_url)
                if not crawler:
                    crawler = prepare_crawler(chapter.url)
                    self._cached_crawlers[base_url] = crawler
                return crawler
            except Exception as e:
                logger.info("Failed with original crawler.", e)

        return None
