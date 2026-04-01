# -*- coding: utf-8 -*-
import logging
import re
from typing import Iterable, Optional

from lncrawl.core import BrowserTemplate, Chapter, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)


class KatReadingCafeCrawler(BrowserTemplate):
    has_mtl = False
    base_url = "https://katreadingcafe.com/"

    auto_create_volumes = False
    novel_title_selector = "h1.page-title, h1.entry-title"
    novel_cover_selector = ",".join(
        [
            ".sertothumb img[src]",
            "[itemprop='image'] img[src]",
            ".post-thumbnail img[src]",
            ".entry-content img[src]",
        ]
    )
    novel_synopsis_selector = ".entry-content p"

    chapter_body_selector = ",".join(
        [
            ".epcontent.entry-content",
            ".entry-content",
        ]
    )

    def initialize(self):
        self.taskman.init_executor(1)
        self.cleaner.bad_tag_text_pairs["a"] = [
            "next chapter",
            "previous chapter",
            "all chapter",
            "next",
            "prev",
            "back",
        ]
        self.cleaner.bad_css.update(
            {
                ".adsbygoogle",
                ".code-block",
                ".site-footer",
                ".sharedaddy",
                "noscript",
                "script",
                "style",
                ".comment-content",
                ".comments-area",
                "div.wp-block-spacer",
                "ins.adsbygoogle",
                "div.jp-relatedposts",
                "nav.post-navigation",
                ".wp-block-buttons",
                ".wp-block-column",
                ".wp-block-spacer",
                "div.site-info",
                "footer",
                "header",
                ".site-header",
                ".site-branding",
                ".main-navigation",
                ".post-navigation",
                ".related-posts",
                "aside",
                ".sidebar",
                ".widget-area",
                ".navimedia",
                ".naveps",
                ".bottomnav",
                ".kofi-button-container",
                ".entry-info",
                ".epheader",
                ".cat-series",
                ".epwrapper > div:not(.epcontent)",
                'div[align="center"]',
                "span[style*='position: absolute']",
            }
        )

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        title = soup.select_one("h1.page-title, h1.entry-title").text
        if "Series:" in title:
            novel.title = title.replace("Series:", "").strip()
        else:
            match = re.search(r"(.*?)[–-]?\s*Chapter\s*\d+", title, re.IGNORECASE)
            novel.title = match.group(1).strip() if match else title

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        meta = soup.select_one('meta[name="author"], meta[property="article:author"]')
        if meta.get("content"):
            novel.author = meta["content"].strip()
            return
        info = soup.select_one(".entry-info .vcard.author .fn")
        if info.text:
            novel.author = info.text
            return
        for p in soup.select(".entry-content p"):
            if re.search(r"(?:author|writer)[:\s]+", p.text, re.IGNORECASE):
                match = re.search(r"(?:author|writer)[:\s]+([^,\r\n]+)", p.text, re.IGNORECASE)
                if match:
                    novel.author = match.group(1).strip()

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        paras = [
            p.text
            for p in soup.select(".entry-content p")[:3]
            if len(p.text.strip()) > 20  # long enough to be a description
        ]
        novel.synopsis = "\n\n".join(paras)

    def parse_volume_tags(self, soup: PageSoup, novel: Novel) -> Iterable[PageSoup]:
        novel.volumes = []
        vols = soup.select(".ts-chl-collapsible")
        conts = soup.select(".ts-chl-collapsible-content")
        if vols and conts and len(vols) == len(conts):
            return reversed(vols)
        return []

    def select_chapter_tags(
        self,
        soup: PageSoup,
        novel: Novel,
        volume: Optional[Volume] = None,
    ) -> Iterable[PageSoup]:
        if volume:
            soup = soup.next_sibling

        chapters = list(soup.select(".eplister ul li a[href]"))
        for a in reversed(chapters):
            if self._valid_chapter_link(a):
                yield a

        if not volume and not chapters:
            links = soup.select(".entry-content a[href]")
            for a in reversed(list(links)):
                if not self._valid_chapter_link(a):
                    continue
                if re.search(r"ch(?:apter)?\.?\s*\d+", a.text.strip(), re.IGNORECASE):
                    yield a

    def _valid_chapter_link(self, link: PageSoup) -> bool:
        href = link.get("href")
        if href not in self.base_url:
            return False
        if "🔒" in link.text:  # locked chapter
            return False
        return True

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        title = soup.text
        url = self.absolute_url(soup["href"])
        num_el = soup.select_one(".epl-num")
        title_el = soup.select_one(".epl-title")
        if num_el and title_el:
            title = f"{num_el.text} - {title_el.text}"
        return Chapter(id=chapter_id, url=url, title=title)
