# -*- coding: utf-8 -*-
import codecs
import logging
import re
import time
from urllib.parse import quote

from bs4.element import NavigableString

from lncrawl.core import Chapter, LegacyCrawler, PageSoup, Volume
from lncrawl.exceptions import LNException

logger = logging.getLogger(__name__)
search_url = "%s/book/searchByPageInShelf?curr=1&limit=10&keyword=%s"
fetch_chapter_list_url = "%s/book/queryIndexList?bookId=%s&curr=1&limit=50000"
max_retries = 5
retry_delays = [15, 30, 60, 120, 180]
chapter_content_delay = 2

genre_slugs = {
    "1": "action",
    "3": "adventure",
    "4": "comedy",
    "7": "light-novel",
    "9": "fantasy",
    "10": "game",
    "11": "gender-bender",
    "12": "harem",
    "13": "historical",
    "14": "horror",
    "16": "martial-arts",
    "17": "mature",
    "18": "mecha",
    "19": "military",
    "20": "mystery",
    "22": "romance",
    "23": "school-life",
    "24": "sci-fi",
    "30": "slice-of-life",
    "32": "sports",
    "33": "supernatural",
    "34": "tragedy",
    "35": "urban-life",
    "36": "wuxia",
    "37": "xianxia",
    "38": "xuanhuan",
    "39": "yaoi",
    "40": "yuri",
    "41": "fanfiction",
}


class NovelHiCrawler(LegacyCrawler):
    base_url = [
        "https://novelhi.com/",
    ]

    def initialize(self):
        self.init_executor(ratelimit=0.25)

    @staticmethod
    def _normalize_slug(value):
        value = str(value or "").strip().lower().replace("'", "").replace("\u2019", "")
        value = re.sub(r"[^a-z0-9]+", "-", value)
        return re.sub(r"-+", "-", value).strip("-")

    def _build_novel_url(self, item):
        genre = genre_slugs.get(str(item.get("primaryGenreId")), "other")
        slug = item.get("novelSlug") or item.get("simpleName") or item.get("bookName")
        return self.absolute_url("/novel/%s/%s" % (genre, self._normalize_slug(slug)))

    def _is_rate_limited(self, error):
        response = getattr(error, "response", None)
        return getattr(response, "status_code", None) == 429 or "429" in repr(error)

    def _retry_after(self, error, attempt):
        response = getattr(error, "response", None)
        value = ""
        if response is not None:
            value = response.headers.get("Retry-After", "")
        if str(value).isdigit():
            return int(value)
        return retry_delays[min(attempt, len(retry_delays) - 1)]

    def _wait_after_429(self, error, attempt, url):
        delay = self._retry_after(error, attempt)
        logger.warning("NovelHi rate limited request. Waiting %ss before retrying: %s", delay, url)
        time.sleep(delay)

    def _get_response_with_retry(self, url, **kwargs):
        last_error = None
        for attempt in range(max_retries):
            try:
                return self.get_response(url, **kwargs)
            except Exception as e:
                if not self._is_rate_limited(e):
                    raise
                last_error = e
                if attempt >= max_retries - 1:
                    break
                self._wait_after_429(e, attempt, url)

        raise LNException("NovelHi request failed after repeated 429 responses") from last_error

    def _get_soup_with_retry(self, url, **kwargs):
        response = self._get_response_with_retry(url, **kwargs)
        self.scraper.last_soup_url = url
        return self.make_soup(response)

    def _get_json_with_retry(self, url, **kwargs):
        last_data = None
        for attempt in range(max_retries):
            response = self._get_response_with_retry(url, **kwargs)
            data = response.json()
            if not self._is_rate_limited_data(data):
                return data
            last_data = data
            if attempt >= max_retries - 1:
                break
            self._wait_after_json_429(data, attempt, url)

        raise LNException("NovelHi request failed after repeated 429 responses: %s" % last_data)

    def _is_rate_limited_data(self, data):
        if not isinstance(data, dict):
            return False

        code = str(data.get("code", ""))
        message = str(data.get("message") or data.get("msg") or "").lower()
        return code == "429" or "too many" in message or "rate limit" in message

    def _wait_after_json_429(self, data, attempt, url):
        delay = retry_delays[min(attempt, len(retry_delays) - 1)]
        logger.warning(
            "NovelHi rate limited JSON request. Waiting %ss before retrying: %s",
            delay,
            url,
        )
        time.sleep(delay)

    def search_novel(self, query):
        data = self.get_json(search_url % (self.scraper.origin, quote(query)))

        results = []
        for item in data["data"]["list"]:
            results.append(
                {
                    "title": item["bookName"],
                    "url": self._build_novel_url(item),
                    "info": "Latest: %s (%s)"
                    % (item["lastIndexName"], item["lastIndexUpdateTime"]),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_book_id = soup.select_one("input#bookId")
        if not possible_book_id:
            raise LNException("NovelHi book id not found")
        self.novel_id = possible_book_id["value"]

        canonical_path = soup.select_one("input#canonicalNovelPath")
        if canonical_path and canonical_path.get("value"):
            self.novel_url = self.absolute_url(canonical_path["value"])

        possible_image = soup.select_one("a.book_cover img.cover")

        self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_title = soup.select_one(".book_info .tit h1")
        if possible_title:
            self.novel_title = possible_title.text.strip()
        else:
            self.novel_title = possible_image["alt"].replace(" | novel cover", "").strip()
        logger.info("Novel title: %s", self.novel_title)

        for span in soup.select(".book_info ul.list span.item"):
            if span.get_text().startswith("Author"):
                author = span.find_next()
                if author:
                    self.novel_author = author.text
        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select_one(".detail-desc")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        data = self.get_json(fetch_chapter_list_url % (self.scraper.origin, self.novel_id))
        for item in reversed(data["data"]["list"]):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.volumes) < vol_id:
                self.volumes.append(Volume(id=vol_id))
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    title=item["indexName"],
                    url="%s/%s" % (self.novel_url.strip("/"), item["indexNum"]),
                    book_id=self.novel_id,
                    book_index_id=item["id"],
                    index_num=item["indexNum"],
                )
            )

    def _extract_chapter_content(self, html, font_obfuscation=False):
        soup = PageSoup.create('<div id="novelhi-content">%s</div>' % html)
        content = soup.select_one("#novelhi-content") or soup
        tag = getattr(content, "tag", content)
        self.cleaner.plain_text_tags.add("sent")

        if font_obfuscation:
            for text in tag.find_all(string=True):
                if isinstance(text, NavigableString) and text.parent.name not in [
                    "script",
                    "style",
                ]:
                    text.replace_with(codecs.decode(str(text), "rot_13"))

        return self.cleaner.extract_contents(tag)

    def download_chapter_body(self, chapter):
        soup = self._get_soup_with_retry(chapter["url"])
        content_path = soup.select_one("input#chapterContentPath")
        content_token = soup.select_one("input#chapterContentToken")

        if content_path and content_token:
            time.sleep(chapter_content_delay)
            content_url = "%s?token=%s" % (
                self.absolute_url(content_path["value"]),
                quote(content_token["value"]),
            )
            data = self._get_json_with_retry(
                content_url,
                headers={
                    "Accept": "application/json, text/plain, */*",
                    "Referer": chapter["url"],
                    "X-Requested-With": "XMLHttpRequest",
                },
            )

            if str(data.get("code")) != "200" or not data.get("data"):
                raise LNException("NovelHi chapter content request failed")

            payload = data["data"]
            if isinstance(payload, str):
                return self._extract_chapter_content(payload)

            font_obfuscation = str(payload.get("fontObfuscation")).lower() == "true"
            font_obfuscation = font_obfuscation or payload.get("fontClass") == "novelhi-chapter-obf"
            return self._extract_chapter_content(
                payload.get("content") or "",
                font_obfuscation=font_obfuscation,
            )

        paras = soup.select("#showReading sent")
        return self._extract_chapter_content("".join(str(p) for p in paras))
