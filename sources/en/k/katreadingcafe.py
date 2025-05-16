# -*- coding: utf-8 -*-
import logging
import re
from typing import Generator, List, Optional, Tuple

from bs4 import BeautifulSoup, Comment, Tag

from lncrawl.models import Chapter
from lncrawl.templates.browser.chapter_only import ChapterOnlyBrowserTemplate

logger = logging.getLogger(__name__)


class KatReadingCafeCrawler(ChapterOnlyBrowserTemplate):
    has_mtl = False
    base_url = "https://katreadingcafe.com/"

    def initialize(self):
        self.init_executor(1)
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
            }
        )

    def _has_base_url(self, href: Optional[str]) -> bool:
        if not href:
            return False
        if isinstance(self.base_url, str):
            return self.base_url in href
        return any(url in href for url in self.base_url)

    def parse_title(self, soup: BeautifulSoup) -> str:
        title = soup.select_one("h1.page-title, h1.entry-title")
        if title:
            text = title.text.strip()
            if "Series:" in text:
                return text.replace("Series:", "").strip()
            match = re.search(r"(.*?)[–-]?\s*Chapter\s*\d+", text, re.IGNORECASE)
            return match.group(1).strip() if match else text
        return "Unknown Title"

    def parse_cover(self, soup: BeautifulSoup) -> Optional[str]:
        selectors = [
            ".sertothumb img",
            "[itemprop='image'] img",
            ".post-thumbnail img",
            ".entry-content img",
        ]
        for sel in selectors:
            img = soup.select_one(sel)
            if img and img.get("src"):
                return self.absolute_url(img["src"])
        return None

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        meta = soup.find("meta", {"name": "author"}) or soup.find(
            "meta", {"property": "article:author"}
        )
        if meta and meta.get("content"):
            yield meta["content"].strip()
            return
        info = soup.select_one(".entry-info .vcard.author .fn")
        if info:
            yield info.text.strip()
            return
        for p in soup.select(".entry-content p"):
            if re.search(r"(?:author|writer)[:\s]+", p.text, re.IGNORECASE):
                match = re.search(
                    r"(?:author|writer)[:\s]+([^,\r\n]+)", p.text, re.IGNORECASE
                )
                if match:
                    yield match.group(1).strip()
                    return

    def parse_description(self, soup: BeautifulSoup) -> Optional[str]:
        paras = [
            p.text.strip()
            for p in soup.select(".entry-content p")[:3]
            if len(p.text.strip()) > 20
        ]
        return "\n\n".join(paras) if paras else None

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        # Unified: pick first parser with results and yield in chronological order
        chapters = (
            self._parse_collapsible_volumes(soup)
            or self._parse_standard_list(soup)
            or self._parse_fallback_links(soup)
        )
        for tag in chapters:
            yield tag

    def _parse_collapsible_volumes(self, soup: BeautifulSoup) -> List[Tag]:
        vols = soup.select(".ts-chl-collapsible")
        conts = soup.select(".ts-chl-collapsible-content")
        if not vols or not conts or len(vols) != len(conts):
            return []
        chapters: List[Tag] = []
        # Reverse volume order so oldest volume is processed first
        for vol_section, vol_content in zip(reversed(vols), reversed(conts)):
            vol_title = vol_section.text.strip()
            # Reverse li list to ensure oldest chapter first within volume
            items = vol_content.select(".eplister ul li")
            for li in reversed(items):
                link = li.select_one("a")
                if self._valid_chapter_link(link):
                    link.attrs["volume"] = vol_title
                    chapters.append(link)
        return chapters

    def _parse_standard_list(self, soup: BeautifulSoup) -> List[Tag]:
        ul = soup.select_one(".eplister ul")
        if not ul:
            return []
        links = [a for a in ul.select("li a") if self._valid_chapter_link(a)]
        # Reverse to get oldest first if site lists newest first
        return list(reversed(links))

    def _parse_fallback_links(self, soup: BeautifulSoup) -> List[Tag]:
        links: List[Tag] = []
        for a in soup.select(".entry-content a"):
            if not self._valid_chapter_link(a):
                continue
            if re.search(r"ch(?:apter)?\.?\s*\d+", a.text.strip(), re.IGNORECASE):
                links.append(a)
        # Sort by chapter number ascending
        links.sort(key=self._extract_chapter_number)
        return links

    def _valid_chapter_link(self, link: Optional[Tag]) -> bool:
        if not link or not link.get("href") or not self._has_base_url(link["href"]):
            return False
        if "🔒" in link.text:
            return False
        return True

    def _extract_chapter_number(self, tag: Tag) -> float:
        href = tag.get("href", "")
        match = re.search(r"chapter[^0-9]*(\d+)", href, re.IGNORECASE) or re.search(
            r"ch(?:apter)?\.?\s*(\d+)", tag.text, re.IGNORECASE
        )
        return float(match.group(1)) if match else float("inf")

    def parse_chapter_item(self, tag: Tag, id: int) -> Optional[Chapter]:
        if "🔒" in tag.text:
            return None
        title, url = self._extract_chapter_info(tag)
        return Chapter(id=id, url=url, title=title)

    def _extract_chapter_info(self, tag: Tag) -> Tuple[str, str]:
        url = self.absolute_url(tag["href"])
        num_el = tag.select_one(".epl-num")
        title_el = tag.select_one(".epl-title")
        if num_el and title_el:
            num = num_el.text.replace("🔒", "").strip()
            title = f"{num} - {title_el.text.strip()}"
        else:
            title = tag.text.strip()
        # Ensure chapter number prefix
        if not re.match(r"^(?:chapter|ch)\.?\s*\d+", title, re.IGNORECASE):
            num = self._extract_chapter_number(tag)
            if num != float("inf"):
                title = f"Chapter {int(num)}: {title}"
        # Include volume info
        vol = tag.get("volume")
        if vol and "Vol" not in title:
            title = f"{vol} {title}"
        return title, url

    def select_chapter_body(self, soup: BeautifulSoup) -> Optional[Tag]:
        content = soup.select_one(".epcontent.entry-content") or soup.select_one(
            ".entry-content"
        )
        if content:
            self._clean_chapter_content(content)
        return content

    def _clean_chapter_content(self, content: Tag):
        # Remove unwanted selectors
        for sel in [
            ".navimedia",
            ".naveps",
            ".bottomnav",
            ".kofi-button-container",
            ".entry-info",
        ]:
            for el in content.select(sel):
                el.decompose()
        # Remove anti-scraping spans
        for span in content.select("span[style*='position: absolute']"):
            span.decompose()
        # Strip weird attributes
        for el in content.select("[aria-5e703], [_63dbbd8], [custom-d9a6e5]"):
            for attr in list(el.attrs):
                del el.attrs[attr]
        # Remove comments and nav links
        for item in content.find_all(text=lambda t: isinstance(t, Comment)):
            item.extract()
        for a in content.select("a"):
            txt = a.text.strip().lower()
            if any(
                x in txt
                for x in (
                    "next chapter",
                    "previous chapter",
                    "all chapter",
                    "next",
                    "prev",
                    "back",
                )
            ):
                a.decompose()
        # Drop empty paragraphs
        for p in content.select("p"):
            if not p.text.strip():
                p.decompose()
