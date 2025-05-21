# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler
# import urllib.parse

logger = logging.getLogger(__name__)


class Novel543(Crawler):
    base_url = ["https://www.novel543.com/"]
    has_manga = False
    has_mtl = False

    # For some reason, only the search page has a anti-bot protection
    # It times out, disabling it for now

    # def search_novel(self, query):
    #     encoded_query = urllib.parse.quote(query)
    #     search_url = f"{self.home_url}search/{encoded_query}"
    #     print(f"Searching for: {query} at {search_url}")
    #     soup = self.get_soup(search_url)
    #     with open("test", "w", encoding="utf-8") as f:
    #         f.write(str(soup))

    #     results = []
    #     if not soup:
    #         logger.error("Failed to get soup from search page: %s", search_url)
    #         return results

    #     list_items = soup.select("ul.list")
    #     if not list_items:
    #         logger.info("No search results found for query: %s", query)
    #         return results

    #     for item in list_items:
    #         title_tag = item.select_one("h3 a[href]")
    #         if title_tag and title_tag.has_attr("href"):
    #             title = title_tag.text.strip()
    #             url = self.absolute_url(title_tag["href"])
    #             desc_tag = item.select_one("p.desc")
    #             if desc_tag:
    #                 desc = desc_tag.text.strip()
    #             else:
    #                 desc = ""

    #             results.append({
    #                 "title": title,
    #                 "url": url,
    #                 "info": desc,
    #             })
    #     logger.info("Found %d novels for query: %s", len(results), query)
    #     return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)
        if not soup:
            logger.error("Failed to get soup from novel page: %s", self.novel_url)
            return

        # Novel Title
        title_tag = soup.select_one("#detail .media-content h1.title")
        if title_tag:
            self.novel_title = title_tag.text.strip()
        else:
            logger.warning("Novel title not found on %s", self.novel_url)

        # Novel Cover
        cover_tag = soup.select_one("#detail .media-left .cover img")
        if cover_tag and cover_tag.has_attr("src"):
            self.novel_cover = self.absolute_url(cover_tag["src"])
        else:
            logger.warning("Novel cover not found on %s", self.novel_url)

        # Novel Author
        author_tag = soup.select_one("#detail .media-content p.meta span.author")
        if author_tag:
            self.novel_author = author_tag.text.strip()
        else:
            # Fallback for author if specific span not found
            author_meta_tag = soup.select_one(
                "#detail .media-content p.meta span:contains('作者：')"
            )
            if author_meta_tag:
                self.novel_author = author_meta_tag.text.replace("作者：", "").strip()
            else:
                logger.warning("Novel author not found on %s", self.novel_url)

        # Novel Synopsis
        synopsis_tag = soup.select_one("#detail .mod .intro")
        if synopsis_tag:
            self.novel_synopsis = self.cleaner.extract_contents(synopsis_tag)
        else:
            logger.warning("Novel synopsis not found on %s", self.novel_url)

        # Chapters
        chapter_list_url = self.absolute_url(self.novel_url.rstrip("/") + "/dir")
        chapter_soup = self.get_soup(chapter_list_url)

        chapter_links = chapter_soup.select("div.chaplist ul.all li a[href]")
        if not chapter_links:
            logger.warning(
                "No chapter links found on %s",
                chapter_list_url if chapter_soup != soup else self.novel_url,
            )
            return

        for idx, a_tag in enumerate(chapter_links):
            chap_title = a_tag.text.strip()
            chap_url = self.absolute_url(a_tag["href"])
            if chap_title and chap_url:
                self.chapters.append(
                    {
                        "id": idx + 1,
                        "volume": 1,
                        "url": chap_url,
                        "title": chap_title,
                    }
                )

        logger.info("Found %d chapters for %s", len(self.chapters), self.novel_title)

    def download_chapter_body(self, chapter):
        """
        Downloads the body of a single chapter.
        """
        soup = self.get_soup(chapter["url"])
        if not soup:
            logger.error("Failed to get soup for chapter: %s", chapter["url"])
            return None

        content_div = soup.select_one("div.chapter-content div.content")
        if not content_div:
            logger.error("No content div found for chapter: %s", chapter["url"])
            return None

        # There's probably a better way to do this with the cleaner, but I forgot how

        # Remove known ad blocks and other unwanted elements
        for ad_block in content_div.select(
            'div.gadBlock, div.adBlock, script, div[style*="text-align: center"] > div[id*="tam-ad"]'
        ):
            ad_block.decompose()

        # Remove "溫馨提示" div
        tip_div = content_div.find("div", style=None, recursive=False)
        if tip_div and "溫馨提示" in tip_div.text:
            tip_div.decompose()

        return self.cleaner.extract_contents(content_div)
