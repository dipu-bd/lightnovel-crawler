# -*- coding: utf-8 -*-
import codecs
import logging
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
browser_wait_timeout = 90
browser_max_retries = 4
browser_retry_delays = [15, 30, 60]
browser_failure_marker = "__NOVELHI_FAILED__"


class NovelHiCrawler(LegacyCrawler):
    base_url = [
        "https://novelhi.com/",
    ]

    def initialize(self):
        self.init_executor(ratelimit=0.25)
        self._chapter_browser = None
        self._chapter_browser_context = None
        self._browser_download_disabled = False

    def close(self):
        self._close_chapter_browser()
        super().close()

    def _close_chapter_browser(self):
        context = getattr(self, "_chapter_browser_context", None)
        browser = getattr(self, "_chapter_browser", None)

        if context:
            try:
                context.__exit__(None, None, None)
            except Exception:
                pass
        elif browser:
            try:
                browser.close()
            except Exception:
                pass

        self._chapter_browser_context = None
        self._chapter_browser = None

    def _get_chapter_browser(self):
        browser = getattr(self, "_chapter_browser", None)
        if browser:
            try:
                if browser.active:
                    return browser
            except Exception:
                pass
            self._close_chapter_browser()

        context = self.create_browser()
        browser = context.__enter__()
        self._chapter_browser_context = context
        self._chapter_browser = browser
        return browser

    def _origin_url(self, path):
        path = str(path or "").strip()
        if path.startswith(("http://", "https://")):
            return path
        if path.startswith("//"):
            scheme = self.scraper.origin.split(":", 1)[0]
            return "%s:%s" % (scheme, path)
        if path.startswith("/"):
            return "%s%s" % (self.scraper.origin.rstrip("/"), path)
        return "%s/%s" % (self.scraper.origin.rstrip("/"), path)

    def _build_novel_url(self, item):
        simple_name = str(item.get("simpleName") or "").strip()
        if simple_name:
            if simple_name.startswith("/") or "/" in simple_name:
                return self._origin_url(simple_name)
            return self._origin_url("/s/%s" % simple_name)

        for key in ["url", "bookUrl", "novelUrl"]:
            value = str(item.get(key) or "").strip()
            if value:
                return self._origin_url(value)

        raise LNException("NovelHi search result missing novel URL")

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
        data = self._get_json_with_retry(search_url % (self.scraper.origin, quote(query)))

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
        soup = self._get_soup_with_retry(self.novel_url)

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

        data = self._get_json_with_retry(
            fetch_chapter_list_url % (self.scraper.origin, self.novel_id)
        )
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

    def _get_browser_chapter_html(self, browser):
        script = """
            (async () => {
                const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));
                const collect = () => {
                    const root = document.querySelector("#showReading");
                    if (!root) return "";

                    const nodes = Array.from(root.querySelectorAll("sent"));
                    const rootText = (root.textContent || "").trim();
                    if (rootText.includes("Chapter loading failed")) {
                        return "%s" + rootText;
                    }
                    if (!nodes.length) return "";

                    const text = nodes
                        .map((node) => node.textContent || "")
                        .join("\\n")
                        .trim();

                    if (text.length < 100) return "";
                    return nodes.map((node) => node.outerHTML).join("");
                };

                const deadline = Date.now() + %d;
                while (Date.now() < deadline) {
                    const html = collect();
                    if (html) return html;
                    await sleep(500);
                }

                return collect();
            })()
        """ % (browser_failure_marker, browser_wait_timeout * 1000)
        return browser.execute_js(script, is_async=True) or ""

    def _has_browser_font_obfuscation(self, browser, html):
        script = """
            (() => {
                const root = document.querySelector("#showReading");
                return Boolean(
                    document.querySelector(".novelhi-chapter-obf") ||
                    (root && root.classList.contains("novelhi-chapter-obf"))
                );
            })()
        """
        return bool(browser.execute_js(script)) or "novelhi-chapter-obf" in html

    def _has_soup_font_obfuscation(self, soup):
        root = soup.select_one("#showReading")
        classes = root.get("class", []) if root else []
        if isinstance(classes, str):
            classes = classes.split()
        return bool(soup.select_one(".novelhi-chapter-obf")) or "novelhi-chapter-obf" in classes

    def _download_chapter_body_with_browser(self, chapter):
        browser = self._get_chapter_browser()
        last_error = ""

        for attempt in range(browser_max_retries):
            browser.visit(chapter["url"])
            browser.wait("#showReading", timeout=browser_wait_timeout)
            time.sleep(chapter_content_delay)

            html = self._get_browser_chapter_html(browser)
            if html.startswith(browser_failure_marker):
                last_error = html.replace(browser_failure_marker, "", 1)
            elif html:
                font_obfuscation = self._has_browser_font_obfuscation(browser, html)
                return self._extract_chapter_content(html, font_obfuscation=font_obfuscation)
            else:
                last_error = "empty chapter content"

            if attempt >= browser_max_retries - 1:
                break

            delay = browser_retry_delays[min(attempt, len(browser_retry_delays) - 1)]
            logger.warning(
                "NovelHi browser did not render chapter content. Waiting %ss before retrying: %s",
                delay,
                chapter["url"],
            )
            time.sleep(delay)

        raise LNException("NovelHi browser did not render chapter content: %s" % last_error)

    def _download_chapter_body_with_api(self, chapter):
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
                return self._extract_chapter_content(
                    payload,
                    font_obfuscation="novelhi-chapter-obf" in payload,
                )

            font_obfuscation = str(payload.get("fontObfuscation")).lower() == "true"
            font_obfuscation = font_obfuscation or payload.get("fontClass") == "novelhi-chapter-obf"
            content = payload.get("content") or ""
            font_obfuscation = font_obfuscation or "novelhi-chapter-obf" in content
            return self._extract_chapter_content(
                content,
                font_obfuscation=font_obfuscation,
            )

        paras = soup.select("#showReading sent")
        if not paras:
            raise LNException("NovelHi chapter content not found")
        return self._extract_chapter_content(
            "".join(str(p) for p in paras),
            font_obfuscation=self._has_soup_font_obfuscation(soup),
        )

    def download_chapter_body(self, chapter):
        if not getattr(self, "_browser_download_disabled", False):
            try:
                return self._download_chapter_body_with_browser(chapter)
            except Exception as e:
                self._browser_download_disabled = True
                self._close_chapter_browser()
                logger.warning(
                    "NovelHi browser download failed. "
                    "Disabling browser downloads for this run and falling back to API: %s",
                    e,
                )

        return self._download_chapter_body_with_api(chapter)
