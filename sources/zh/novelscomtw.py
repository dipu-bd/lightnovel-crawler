import re
from typing import List, Set
from urllib.parse import urlsplit

from lncrawl.core import Chapter, SoupTemplate
from lncrawl.exceptions import LNException


class NovelsComTwCrawler(SoupTemplate):
    base_url = ["https://www.novels.com.tw/"]
    language = "zh"
    request_rate_limit = 1

    novel_title_selector = ".novel_info_title h1"
    novel_cover_selector = ".novel_info_main > img"
    novel_author_selector = ".novel_info_title a[href^='/author/']"
    novel_tags_selector = ".novel_info_title p > span:first-child"
    novel_synopsis_selector = "#info .intro"

    # The recent-chapters panel is a duplicate, in reverse order.
    chapter_list_selector = "#catalog .chapters a[href]"
    chapter_body_selector = "#article"

    def download_chapter(self, chapter: Chapter) -> None:
        url = self.build_chapter_url(chapter)
        initial = urlsplit(url)
        stem = re.sub(r"(?:_\d+)?\.html$", "", initial.path)
        visited: Set[str] = set()
        parts: List[str] = []

        while True:
            if url in visited:
                raise LNException("Chapter pagination repeats a page")
            visited.add(url)

            # The served HTML contains only an encoded payload and a placeholder.
            # The site's script replaces #article with paragraphs when it is ready.
            for _ in range(3):
                soup = self.scraper.render_soup(url, wait_for="#article > p")
                article = soup.select_one(self.chapter_body_selector)
                # A render snapshot can precede the script's DOM replacement.
                if article.select("p") and not article.select("#chapter-content"):
                    break
            else:
                raise LNException("Chapter text did not finish rendering")

            body = self.cleaner.extract_contents(article)
            if not body:
                raise LNException("Chapter text did not load")
            parts.append(body)

            next_tag = soup.select_one("#next_url")
            if next_tag.text.strip() not in ("下一頁", "下一页"):
                break

            # Ads may rewrite href; the site's own keyboard navigation uses this attribute.
            href = next_tag.get("data-real-href") or next_tag.get("href")
            next_url = self.absolute_url(href, page_url=url)
            target = urlsplit(next_url)
            if target.netloc != initial.netloc or not re.fullmatch(
                rf"{re.escape(stem)}_\d+\.html", target.path
            ):
                raise LNException("Invalid next page for this chapter")
            url = next_url

        chapter.body = "\n".join(parts)
