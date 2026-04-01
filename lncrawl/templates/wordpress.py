"""Madara / wp-manga theme over HTTP using SoupTemplate (no browser)."""

from typing import Iterable, Optional
from urllib.parse import quote, quote_plus, urlencode

from ..context import ctx
from ..core import Chapter, Novel, PageSoup, SoupTemplate, Volume
from ..exceptions import LNException


class WordpressTemplate(SoupTemplate):
    """Shared Madara-style selectors and chapter loading (ajax + admin-ajax fallback)."""

    is_template = True
    can_search = True

    #: If True, chapter body is "".join(str(p) for p in soup.select(".reading-content p")).
    madara_body_from_paragraphs = False

    #: None, "quote", or "quote_plus" for the search query encoding.
    madara_search_quote_mode: Optional[str] = None

    #: If > 0, cap search tab results (some sites return huge lists).
    madara_search_max_results = 0

    search_item_list_selector = ".c-tabs-item__content"
    search_item_title_selector = ".post-title h3 a, .post-title h4 a"
    search_item_url_selector = ".post-title h3 a, .post-title h4 a"

    novel_title_selector = ".post-title h1"
    novel_cover_selector = ".summary_image a img"
    novel_author_selector = '.author-content a[href*="manga-author"]'
    novel_tags_selector = '.genres-content a[rel="tag"]'
    novel_synopsis_selector = ".description-summary"

    chapter_list_selector = "li.wp-manga-chapter a"
    chapter_body_selector = "div.reading-content"

    madara_search_extra: dict = {}

    def build_search_url(self, query: str) -> str:
        if self.madara_search_quote_mode == "quote":
            q = quote(query.lower())
        elif self.madara_search_quote_mode == "quote_plus":
            q = quote_plus(query.lower())
        else:
            q = query.lower().replace(" ", "+")
        params = {
            "s": q,
            "post_type": "wp-manga",
            "op": "",
            "author": "",
            "artist": "",
            "release": "",
            "adult": "",
        }
        params.update(self.madara_search_extra)
        return f"{self.scraper.origin}?{urlencode(params)}"

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        items = list(super().select_search_item_list(query))
        if self.madara_search_max_results:
            return items[: self.madara_search_max_results]
        return items

    def parse_search_item_info(self, soup: PageSoup) -> str:
        latest = soup.select_one(".latest-chap .chapter a")
        votes = soup.select_one(".rating .total_votes")
        return "%s | Rating: %s" % (latest.text, votes.text)

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])
        self.cleaner.bad_css.update(['a[href="javascript:void(0)"]'])

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_title_selector)
        for span in tag.select("span"):
            span.extract()
        novel.title = tag.text.strip()

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        cover_tag = soup.select_one(self.novel_cover_selector)
        if not cover_tag:
            return
        src_url = cover_tag.get("data-src") or cover_tag.get("src")
        novel.cover_url = self.absolute_url(src_url) if src_url else ""

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        tag = soup.select_one(self.novel_synopsis_selector)
        novel.synopsis = self.cleaner.extract_contents(tag) if tag else ""

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        try:
            clean_novel_url = novel.url.split("?")[0].strip("/")
            response = self.scraper.submit_form(f"{clean_novel_url}/ajax/chapters/")
            ch_soup = self.scraper.make_soup(response)
            chapters = ch_soup.select(self.chapter_list_selector)
            return reversed(list(chapters))
        except Exception:
            ctx.logger.debug("Failed to fetch chapters using ajax", exc_info=True)

        nl_id = soup.select_one("#manga-chapters-holder[data-id]")
        if not nl_id:
            raise LNException("No chapter id tag found for alternate method")

        try:
            response = self.scraper.submit_form(
                f"{self.scraper.origin}wp-admin/admin-ajax.php",
                data={
                    "action": "manga_get_chapters",
                    "manga": nl_id["data-id"],
                },
            )
            ch_soup = self.scraper.make_soup(response)
            chapters = ch_soup.select(self.chapter_list_selector)
            return reversed(list(chapters))
        except Exception as e:
            raise LNException("Failed to fetch chapters using alternate method") from e

    def download_chapter(self, chapter: Chapter) -> None:
        if self.madara_body_from_paragraphs:
            url = self.build_chapter_url(chapter)
            soup = self.scraper.get_soup(url)
            paragraphs = soup.select(".reading-content p")
            chapter.body = "".join(str(p) for p in paragraphs)
            return
        super().download_chapter(chapter)


class WordpressMangaTemplate(WordpressTemplate):
    """Madara theme with lazy-loaded images in chapter HTML (common on manga sources)."""

    is_template = True
    has_manga = True

    def download_chapter(self, chapter: Chapter) -> None:
        if self.madara_body_from_paragraphs:
            super().download_chapter(chapter)
            return
        url = self.build_chapter_url(chapter)
        soup = self.scraper.get_soup(url)
        body = soup.select_one(self.chapter_body_selector)
        if not body:
            chapter.body = ""
            return
        for img in body.find_all("img"):
            if img.get("data-src"):
                src_url = img["data-src"]
                parent = img.parent
                if parent:
                    img.extract()
                    parent.append(soup.new_tag("img", src=src_url))
            elif img.get("src"):
                src_url = img["src"]
                parent = img.parent
                if parent:
                    img.extract()
                    parent.append(soup.new_tag("img", src=src_url))
        self.parse_chapter_body(body, chapter)
