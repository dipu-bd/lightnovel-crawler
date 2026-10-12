# -*- coding: utf-8 -*-
import html
import logging
import math
import re
from typing import Dict, Iterable, Optional, Set
from urllib.parse import urlencode, urlsplit

from scraper import PageSoup

from lncrawl.core import Chapter, Novel, SoupTemplate, Volume
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)

# Simple Membership plugin: what it renders in place of a members-only post's content.
LOCKED_RE = re.compile(r"logged in to view this content", re.I)


class LoreNovelsCrawler(SoupTemplate):
    base_url = ["https://lorenovels.com/"]

    novel_cover_selector = 'meta[property="og:image"]'
    novel_synopsis_selector = ".entry-content > .wp-block-group > p"

    # A WordPress "Latest Posts" block on the novel page, newest first.
    chapter_list_selector = "ul.wp-block-latest-posts__list li a[href]"
    chapter_list_reverse = True

    chapter_body_selector = ".entry-content"

    def initialize(self) -> None:
        # The Index/Next buttons sit inside the post content.
        self.cleaner.bad_css.update({".wp-block-buttons"})

    # The novel is a plain page: "Title:", "Author:", "Genre:" and "Status:" rows, label then value.
    def _info(self, soup: PageSoup) -> Dict[str, str]:
        info: Dict[str, str] = {}
        for row in soup.select(".entry-content .wp-block-group.is-vertical"):
            label, sep, value = row.text.partition(":")
            if sep and value.strip():
                info[label.strip().lower()] = value.strip()
        return info

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        novel.title = self._info(soup).get("title", "")
        if not novel.title:
            novel.title = re.sub(r"\s*-\s*Lorenovels\s*$", "", soup.select_one("title").text)

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        novel.author = self._info(soup).get("author", "")

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        genre = self._info(soup).get("genre", "")
        novel.tags = [t.strip() for t in genre.split(",") if t.strip()]

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        novel.synopsis = "".join(
            f"<p>{html.escape(p.text)}</p>" for p in soup.select(self.novel_synopsis_selector)
        )

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        super().parse_toc(soup, novel)
        locked = self._locked_urls(novel)
        if locked:
            logger.info(f"Skipping {len(locked)} members-only chapters")
            novel.chapters = [c for c in novel.chapters if _key(c.url) not in locked]

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        if not tag.select(self.chapter_list_selector):
            raise LNException("Chapter list not found on the novel page")
        return super().select_chapter_tags(tag, novel, volume)

    # The list does not mark members-only chapters; the REST excerpt of one is the login prompt.
    def _locked_urls(self, novel: Novel) -> Set[str]:
        if not novel.chapters:
            return set()
        try:
            slug = urlsplit(novel.chapters[0].url).path.strip("/")
            posts = self._wp_json("posts", slug=slug, _fields="categories")
            if not posts or not posts[0].get("categories"):
                logger.warning(f"No category found for {novel.chapters[0].url}")
                return set()
            category = posts[0]["categories"][0]

            locked: Set[str] = set()
            per_page = 100
            for page in range(1, math.ceil(len(novel.chapters) / per_page) + 1):
                posts = self._wp_json(
                    "posts",
                    categories=category,
                    per_page=per_page,
                    page=page,
                    _fields="link,excerpt",
                )
                for post in posts:
                    if LOCKED_RE.search(post["excerpt"]["rendered"]):
                        locked.add(_key(post["link"]))
                if len(posts) < per_page:
                    break
            return locked
        except Exception as e:
            # Members-only chapters still raise on download, so this only costs failed chapters.
            logger.warning(f"Could not detect members-only chapters: {e!r}")
            return set()

    def _wp_json(self, route: str, **params: object) -> list:
        return self.scraper.get_json(
            self.absolute_url(f"/wp-json/wp/v2/{route}?{urlencode(params)}")
        )

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        if soup.select_one(".swpm-post-not-logged-in-msg"):
            raise LNException(f"Chapter is members-only: {chapter.url}")
        super().parse_chapter_body(soup, chapter)


def _key(url: str) -> str:
    return urlsplit(url).path.strip("/")
