# -*- coding: utf-8 -*-

import json
import logging
import re
from typing import Callable, Generator, Optional
from urllib.parse import quote_plus, urlencode

from lncrawl.core import Chapter, SearchResult
from lncrawl.exceptions import FallbackToBrowser, LNException
from lncrawl.templates.browser.basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)


class NoveLightCrawler(BasicBrowserTemplate):
    base_url = "https://novelight.net/"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["div.advertisment"])

    def _ensure_browser_ready(self):
        if not self.browser.current_url or not str(self.browser.current_url).startswith(self.home_url):
            self.browser.visit(self.home_url)

    def _browser_get_json(self, url: str, headers: Optional[dict] = None, **_kwargs):
        self._ensure_browser_ready()
        headers = headers or {}
        script = """
            const url = arguments[0];
            const headers = arguments[1] || {};
            const callback = arguments[arguments.length - 1];
            fetch(url, {credentials: 'include', headers})
              .then(r => r.text())
              .then(t => callback(t))
              .catch(e => callback(JSON.stringify({__error__: String(e)})));
        """
        text = self.browser.execute_js(script, url, headers, is_async=True)
        if not text:
            raise LNException(f"Empty response from {url}")
        try:
            data = json.loads(text)
        except Exception as e:
            raise LNException(f"Invalid JSON from {url}: {e}")
        if isinstance(data, dict) and data.get("__error__"):
            raise LNException(f"Browser fetch error for {url}: {data['__error__']}")
        return data

    def _parse_search_results(self, soup) -> Generator[SearchResult, None, None]:
        yield from [
            SearchResult(title=a.text.strip(), url=self.absolute_url(a["href"]))
            for a in soup.select(".manga-grid-list a.item")
            if a
        ]

    def search_novel_in_soup(self, query) -> Generator[SearchResult, None, None]:
        soup = self.get_soup(f"{self.home_url}catalog/?search={quote_plus(query.lower())}")
        yield from self._parse_search_results(soup)

    def search_novel_in_browser(self, query) -> Generator[SearchResult, None, None]:
        self.browser.visit(f"{self.home_url}catalog/?search={quote_plus(query.lower())}")
        yield from self._parse_search_results(self.browser.soup)

    def _extract_book_tokens(self, soup):
        page_scripts = soup.select("body > script:not([src])")
        scripts_joined = "\n".join(str(s) for s in page_scripts)
        book_id_match = re.search(r'.*const BOOK_ID = "(\d+)".*', scripts_joined)
        if not book_id_match:
            raise LNException("Could not extract book_id from novel page")
        book_id = book_id_match.group(1)
        csrf_match = re.search(r'.*window.CSRF_TOKEN = "(\w+)".*', scripts_joined)
        if not csrf_match:
            raise LNException("Could not extract csrfmiddlewaretoken from novel page")
        csrfmiddlewaretoken = csrf_match.group(1)
        return book_id, csrfmiddlewaretoken

    def _read_novel_info(self, soup, json_get: Callable):
        title_tag = soup.select_one("header.header-manga h1")
        if not title_tag:
            raise LNException("No title found")
        self.novel_title = title_tag.get_text().strip()
        logger.info("Novel title: %s", self.novel_title)

        novel_cover = soup.select_one("div.second-information div.poster img")
        if novel_cover:
            self.novel_cover = self.absolute_url(novel_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        novel_synopsis = soup.select_one("div#information section.text-info")
        if novel_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(novel_synopsis)

        novel_tags = soup.select("div#information section.tags a[href^='/catalog/?tags=']")
        for tag in novel_tags:
            self.novel_tags.append(tag.get_text().strip())

        novel_author = soup.select_one(".mini-info a[href^='/character/'] div.info")
        if novel_author and novel_author.get_text():
            self.novel_author = novel_author.get_text().strip()
        logger.info("Novel author: %s", self.novel_author)

        book_id, csrfmiddlewaretoken = self._extract_book_tokens(soup)
        logger.debug("book_id: %s", book_id)
        logger.debug("csrfmiddlewaretoken: %s", csrfmiddlewaretoken)

        headers = {
            "Accept": "*/*",
            "Referer": self.novel_url,
            "x-requested-with": "XMLHttpRequest",
        }
        chapters_lists = soup.select("select#select-pagination-chapter > option")
        bar = self.progress_bar(total=len(chapters_lists), desc="Chapters list", unit="page")
        encountered_paid_chapter = False
        for page in reversed(chapters_lists):
            if encountered_paid_chapter:
                continue
            params = {
                "csrfmiddlewaretoken": csrfmiddlewaretoken,
                "book_id": book_id,
                "page": page["value"],
            }
            chapters_response = json_get(
                f"{self.home_url}book/ajax/chapter-pagination?{urlencode(params)}",
                headers=headers,
            )
            chapters_soup = self.make_soup(chapters_response["html"])
            for a in reversed(chapters_soup.select("a[href^='/book/chapter/']")):
                if a.select_one(".chapter-info .cost"):
                    encountered_paid_chapter = True
                    continue
                title = a.select_one(".title")
                self.chapters.append(
                    Chapter(
                        id=len(self.chapters) + 1,
                        url=self.absolute_url(a["href"]),
                        title=(title or a).get_text(strip=True),
                    )
                )
            bar.update()
        bar.close()
        if encountered_paid_chapter:
            logger.warning("WARNING: Paid chapters are not supported and will be skipped.")

    def read_novel_info_in_soup(self):
        try:
            soup = self.get_soup(self.novel_url)
            self._read_novel_info(soup, self.get_json)
        except Exception as e:
            raise FallbackToBrowser() from e

    def read_novel_info_in_browser(self):
        self.browser.visit(self.novel_url)
        self.browser.wait("header.header-manga h1", timeout=30)
        self._read_novel_info(self.browser.soup, self._browser_get_json)

    def _download_chapter_body(self, chapter: Chapter, json_get: Callable):
        headers = {
            "Accept": "*/*",
            "Referer": chapter.url,
            "x-requested-with": "XMLHttpRequest",
        }

        soup = self.make_soup(json_get(chapter.url.replace("chapter", "ajax/read-chapter"), headers=headers)["content"])

        contents = soup.select_one(".chapter-text")
        self.cleaner.clean_contents(contents)

        return str(contents)

    def download_chapter_body_in_soup(self, chapter: Chapter):
        try:
            return self._download_chapter_body(chapter, self.get_json)
        except Exception as e:
            raise FallbackToBrowser() from e

    def download_chapter_body_in_browser(self, chapter: Chapter):
        return self._download_chapter_body(chapter, self._browser_get_json)
