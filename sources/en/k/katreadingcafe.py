# -*- coding: utf-8 -*-
import logging
import re
from typing import Generator

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
                "div.sharedaddy",
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
                ".navigation",
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

    def _has_base_url(self, href: str) -> bool:
        """Helper method to check if href contains the base URL, handling both string and list types"""
        if not href:
            return False

        base_url = self.base_url
        if isinstance(base_url, str):
            return base_url in href
        elif isinstance(base_url, list):
            return any(url in href for url in base_url)
        return False

    def parse_title(self, soup: BeautifulSoup) -> str:
        # For series page
        possible_title = soup.select_one("h1.page-title")
        if possible_title and "Series:" in possible_title.text:
            return possible_title.text.replace("Series:", "").strip()

        # For chapter page fallback
        possible_title = soup.select_one("h1.entry-title")
        if possible_title:
            title_text = possible_title.text.strip()
            # Extract novel name from chapter title if possible
            match = re.search(r"(.*?)[–-]\s*Chapter\s+\d+", title_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            # Second pattern attempt
            match = re.search(r"(.*?)\s+Chapter\s+\d+", title_text, re.IGNORECASE)
            if match:
                return match.group(1).strip()

            return title_text

        return "Unknown Title"

    def parse_cover(self, soup: BeautifulSoup) -> str:
        # Check for cover image in sertothumb div (new format)
        possible_image = soup.select_one(".sertothumb img")
        if possible_image and "src" in possible_image.attrs:
            return self.absolute_url(possible_image["src"])

        # Check for cover image using itemprop attribute
        possible_image = soup.select_one("[itemprop='image'] img")
        if possible_image and "src" in possible_image.attrs:
            return self.absolute_url(possible_image["src"])

        # Check for cover image in series page (original method)
        possible_image = soup.select_one(".post-thumbnail img")
        if possible_image and "src" in possible_image.attrs:
            return self.absolute_url(possible_image["src"])

        # Fallback to first content image
        possible_image = soup.select_one(".entry-content img")
        if possible_image and "src" in possible_image.attrs:
            return self.absolute_url(possible_image["src"])

        return None

    def parse_authors(self, soup: BeautifulSoup) -> Generator[str, None, None]:
        # Author info might be in the content or metadata
        author_meta = soup.find("meta", {"name": "author"}) or soup.find(
            "meta", {"property": "article:author"}
        )
        if author_meta and author_meta.get("content"):
            yield author_meta.get("content").strip()
            return

        # Check for author in the entry-info
        author_info = soup.select_one(".entry-info .vcard.author .fn")
        if author_info:
            yield author_info.text.strip()
            return

        # Look for author in visible content
        content = soup.select_one(".entry-content")
        if content:
            author_line = None
            for p in content.select("p"):
                text = p.text.strip().lower()
                if "author" in text or "writer" in text:
                    author_line = p.text.strip()
                    break

            if author_line:
                author_match = re.search(
                    r"(?:author|writer)[:\s]+([^,\r\n]+)", author_line, re.IGNORECASE
                )
                if author_match:
                    yield author_match.group(1).strip()

    def parse_description(self, soup: BeautifulSoup) -> str:
        # Description is usually in the first few paragraphs
        content = soup.select_one(".entry-content")
        if content:
            paragraphs = []
            for p in content.select("p")[:3]:  # Take first 3 paragraphs
                if len(p.text.strip()) > 20:  # Only include non-trivial paragraphs
                    paragraphs.append(p.text.strip())

            if paragraphs:
                return "\n\n".join(paragraphs)

        return None

    def select_chapter_tags(self, soup: BeautifulSoup) -> Generator[Tag, None, None]:
        """Extract all chapter links and return them in chronological order (oldest first)"""
        chapter_links = []

        # Check for collapsible volume structure (ts-chl-collapsible elements)
        volume_sections = soup.select(".ts-chl-collapsible")
        volume_contents = soup.select(".ts-chl-collapsible-content")

        if (
            volume_sections
            and volume_contents
            and len(volume_sections) == len(volume_contents)
        ):
            # We found a volume structure - parse each volume
            all_volumes_chapters = []

            # Process each volume and its chapters (in reverse to get oldest volume first)
            for i in range(len(volume_sections) - 1, -1, -1):
                vol_title = volume_sections[i].text.strip()
                vol_content = volume_contents[i]
                volume_chapters = []

                # Find all chapter links in this volume
                chapter_list = vol_content.select_one(".eplister ul")
                if chapter_list:
                    for li in chapter_list.select("li"):
                        link = li.select_one("a")
                        if (
                            link
                            and link.get("href")
                            and self._has_base_url(link.get("href"))
                        ):
                            # Check if the chapter is locked
                            chapter_num_div = link.select_one(".epl-num")
                            if chapter_num_div and "🔒" in chapter_num_div.text:
                                # Skip locked chapters
                                continue

                            # Store volume info with the link for later use
                            link.attrs["volume"] = vol_title
                            volume_chapters.append(link)

                # Add chapters in reverse order (so oldest chapter first)
                all_volumes_chapters.extend(reversed(volume_chapters))

            # Return all chapters in correct order (oldest volume's oldest chapter first)
            for link in all_volumes_chapters:
                yield link
            return

        # Standard eplister format (non-volume structure)
        chapter_links = []
        chapter_list = soup.select_one(".eplister ul")
        if chapter_list:
            for li in chapter_list.select("li"):
                link = li.select_one("a")
                if link and link.get("href") and self._has_base_url(link.get("href")):
                    # Check if the chapter is locked
                    chapter_num_div = link.select_one(".epl-num")
                    if chapter_num_div and "🔒" in chapter_num_div.text:
                        # Skip locked chapters
                        continue
                    chapter_links.append(link)

            # Return chapters in chronological order
            for link in reversed(chapter_links):
                yield link
            return

        # Fallback to old format (links in content)
        chapter_links = []
        content = soup.select_one(".entry-content")
        if content:
            for link in content.select("a"):
                href = link.get("href", "")
                if not href or not self._has_base_url(href):
                    continue

                # Skip locked chapters
                if "🔒" in link.text:
                    continue

                # Match chapter links by text or URL pattern
                text = link.text.strip().lower()
                if (
                    "ch." in text
                    or "chapter" in text
                    or re.search(r"ch\.?\s*\d+", text, re.IGNORECASE)
                    or re.search(r"chapter\s*\d+", text, re.IGNORECASE)
                ):
                    chapter_links.append(link)

            # Try to extract chapter numbers for sorting
            def get_chapter_num(link):
                href = link.get("href", "")
                # Try to find chapter number in URL
                match = re.search(r"chapter[^0-9]*(\d+)", href.lower())
                if match:
                    return int(match.group(1))
                # Try to find in text
                match = re.search(r"chapter[^0-9]*(\d+)", link.text.lower())
                if match:
                    return int(match.group(1))
                # Default to a high number to put at the end
                return 999999

            # Sort by chapter number
            chapter_links.sort(key=get_chapter_num)

            for link in chapter_links:
                yield link

    def parse_chapter_item(self, tag: Tag, id: int) -> Chapter:
        chapter_url = self.absolute_url(tag["href"])
        volume_info = tag.get("volume", "")  # Get volume info if available

        # Handle the new chapter format
        num_div = tag.select_one(".epl-num")
        title_div = tag.select_one(".epl-title")

        if num_div and title_div:
            # This is the new format
            chapter_num = num_div.text.strip().replace("🔒", "").strip()
            chapter_title = f"{chapter_num} - {title_div.text.strip()}"
        else:
            # Fallback to old format
            chapter_title = tag.text.strip()

        # Skip locked chapters
        if "🔒" in tag.text:
            return None

        # Clean up and format chapter title if needed
        if len(chapter_title) < 3 or chapter_title.isdigit():
            # Extract from URL if title is too short
            url_parts = chapter_url.split("/")
            if url_parts:
                slug = url_parts[-2] if url_parts[-1] == "" else url_parts[-1]
                slug = slug.replace("-", " ").title()
                # Extract chapter number if present
                chapter_num_match = re.search(r"Chapter (\d+)", slug, re.IGNORECASE)
                if chapter_num_match:
                    chapter_title = slug
                else:
                    # Try to find chapter number in URL
                    url_match = re.search(r"chapter-(\d+)", chapter_url.lower())
                    if url_match:
                        chapter_num = url_match.group(1)
                        chapter_title = f"Chapter {chapter_num}"

                        # Include arc name if possible
                        arc_match = re.search(
                            r"(the-[^-]+-and-[^-]+)", chapter_url.lower()
                        )
                        if arc_match:
                            arc_name = arc_match.group(1).replace("-", " ").title()
                            chapter_title += f" - {arc_name}"
                    else:
                        chapter_title = slug

        # Make sure chapter number is included
        chapter_match = re.search(
            r"chapter\s*(\d+)|ch\.\s*(\d+)", chapter_title.lower()
        )
        if not chapter_match:
            # Try to find chapter number in URL
            url_match = re.search(r"chapter-(\d+)|ch-(\d+)", chapter_url.lower())
            if url_match:
                chapter_num = url_match.group(1) or url_match.group(2)
                if not chapter_title.lower().startswith(
                    "chapter"
                ) and not chapter_title.lower().startswith("ch."):
                    chapter_title = f"Chapter {chapter_num}: {chapter_title}"

        # Include volume information in the chapter title if available
        if volume_info and "Vol" not in chapter_title:
            chapter_title = f"{volume_info} {chapter_title}"

        return Chapter(
            id=id,
            url=chapter_url,
            title=chapter_title,
        )

    def select_chapter_body(self, soup: BeautifulSoup) -> Tag:
        # Find main chapter content
        content = soup.select_one(".epcontent.entry-content")
        if not content:
            content = soup.select_one(".entry-content")

        if content:
            # Remove navigation elements at top and bottom
            for nav in content.select(".navimedia, .naveps, .bottomnav"):
                nav.decompose()

            # Remove donation/ko-fi button
            for kofi in content.select(".kofi-button-container"):
                kofi.decompose()

            # Remove entry info (author, views, date)
            for info in content.select(".entry-info"):
                info.decompose()

            # Remove hidden spans used for anti-scraping
            for span in content.select(
                "span[style*='position: absolute; height: 0; width: 0; overflow: hidden;']"
            ):
                span.decompose()

            # Remove elements with weird attributes (anti-scraping)
            for el in content.select("[aria-5e703], [_63dbbd8], [custom-d9a6e5]"):
                # Just remove the attribute but keep the text
                for attr in list(el.attrs.keys()):
                    del el.attrs[attr]

            # Remove any comments
            for comment in content.find_all(
                text=lambda text: isinstance(text, Comment)
            ):
                comment.extract()

            # Remove next/prev links
            for link in content.select("a"):
                link_text = link.text.strip().lower()
                if (
                    "next chapter" in link_text
                    or "previous chapter" in link_text
                    or "chapter" in link_text
                    and any(x in link_text for x in ["next", "prev", "back"])
                    or "all chapter" in link_text.lower()
                ):
                    link.decompose()

            # Clean up empty paragraphs
            for p in content.select("p"):
                if not p.text.strip():
                    p.decompose()

        return content
