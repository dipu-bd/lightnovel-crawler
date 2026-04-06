# -*- coding: utf-8 -*-
import logging
import re

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class ShuhaigeCrawler(LegacyCrawler):
    base_url = "https://m.shuhaige.net/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # Extract novel title from the detail section
        possible_title = soup.select_one(".detail .name strong")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # Extract novel cover
        possible_novel_cover = soup.select_one(".detail img")
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # Extract author
        possible_novel_author = soup.select_one(".detail .author a")
        if possible_novel_author:
            self.novel_author = possible_novel_author.text.strip()
        logger.info("Novel author: %s", self.novel_author)

        # Extract synopsis from the intro section
        possible_synopsis = soup.select_one(".intro p")
        if possible_synopsis:
            # Clean up the synopsis text
            synopsis_text = possible_synopsis.get_text(strip=True)
            # Remove author info and book links at the end
            synopsis_lines = synopsis_text.split("\n")
            clean_synopsis = []
            for line in synopsis_lines:
                line = line.strip()
                if (
                    line
                    and not line.startswith("是一名出色的小说作者")
                    and not line.startswith("最新章节")
                ):
                    clean_synopsis.append(line)
            self.novel_synopsis = "\n".join(clean_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        # Get the book ID from the URL - handle both formats
        book_id_match = re.search(r"shu_(\d+)\.html", self.novel_url)
        if not book_id_match:
            # Try the chapter list URL format
            book_id_match = re.search(r"/(\d+)/?", self.novel_url)
            if book_id_match:
                book_id = book_id_match.group(1)
                # If we got the chapter list URL, we need to get novel info from the main page
                main_novel_url = f"https://m.shuhaige.net/shu_{book_id}.html"
                logger.debug("Converting chapter list URL to novel URL: %s", main_novel_url)
                soup = self.get_soup(main_novel_url)

                # Re-extract novel info from the proper novel page
                possible_title = soup.select_one(".detail .name strong")
                if possible_title:
                    self.novel_title = possible_title.text.strip()
                    logger.info("Novel title: %s", self.novel_title)

                possible_novel_cover = soup.select_one(".detail img")
                if possible_novel_cover:
                    self.novel_cover = self.absolute_url(possible_novel_cover["src"])
                logger.info("Novel cover: %s", self.novel_cover)

                possible_novel_author = soup.select_one(".detail .author a")
                if possible_novel_author:
                    self.novel_author = possible_novel_author.text.strip()
                logger.info("Novel author: %s", self.novel_author)

                possible_synopsis = soup.select_one(".intro p")
                if possible_synopsis:
                    synopsis_text = possible_synopsis.get_text(strip=True)
                    synopsis_lines = synopsis_text.split("\n")
                    clean_synopsis = []
                    for line in synopsis_lines:
                        line = line.strip()
                        if (
                            line
                            and not line.startswith("是一名出色的小说作者")
                            and not line.startswith("最新章节")
                        ):
                            clean_synopsis.append(line)
                    self.novel_synopsis = "\n".join(clean_synopsis)
                logger.info("Novel synopsis: %s", self.novel_synopsis)
            else:
                raise Exception("Could not extract book ID from URL")
        else:
            book_id = book_id_match.group(1)

        # Get all chapters from all pages
        all_chapter_links = []
        page_num = 1

        while True:
            if page_num == 1:
                chapter_list_url = f"https://m.shuhaige.net/{book_id}/"
            else:
                chapter_list_url = f"https://m.shuhaige.net/{book_id}_{page_num}/"

            logger.debug("Visiting chapter list page %d: %s", page_num, chapter_list_url)
            chapter_soup = self.get_soup(chapter_list_url)

            # Extract chapters from current page
            chapter_links = chapter_soup.select(".read li a")

            if not chapter_links:
                # No more chapters, break the loop
                break

            all_chapter_links.extend(chapter_links)

            # Check if there's a next page by looking at pagination
            next_page_links = chapter_soup.select(".pagelist a")
            has_next_page = False

            for link in next_page_links:
                if "下一页" in link.get_text(strip=True):
                    # Make sure it's not disabled or pointing to current page
                    href = link.get("href", "")
                    if href and not href.endswith(f"_{page_num}/"):
                        has_next_page = True
                        break

            if not has_next_page:
                break

            page_num += 1

        volumes = set([])

        for a in all_chapter_links:
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)

            chapter_title = a.get_text(strip=True)
            chapter_url = self.absolute_url(a["href"])

            self.chapters.append(
                Chapter(id=ch_id, volume=vol_id, title=chapter_title, url=chapter_url)
            )

        self.volumes = [Volume(id=x, title=f"Volume {x}") for x in sorted(volumes)]
        logger.info("Found %d chapters in %d volumes", len(self.chapters), len(self.volumes))

    def download_chapter_body(self, chapter):
        logger.debug("Downloading chapter: %s", chapter["url"])
        soup = self.get_soup(chapter["url"])

        # Extract content from the content div
        contents = soup.select_one(".content")
        if not contents:
            # Fallback to other possible content containers
            contents = soup.select_one("#content") or soup.select_one(".chapter_content")

        if not contents:
            logger.warning("Could not find content for chapter: %s", chapter["title"])
            return ""

        # Clean up the content
        # Remove promotional text at the end
        for p in contents.find_all("p"):
            text = p.get_text(strip=True)
            if (
                "这章没有结束" in text
                or "无错的章节将持续" in text
                or "喜欢【崩坏世界】我能预知未来请大家收藏" in text
                or "书海阁小说网更新速度全网最快" in text
            ):
                p.decompose()

        return self.cleaner.extract_contents(contents)
