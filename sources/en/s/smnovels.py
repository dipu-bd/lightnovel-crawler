# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class SMNovelsCrawler(LegacyCrawler):
    base_url = "https://smnovels.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)

        page_url = self.novel_url.rstrip("/") + "/"
        page_no = 1
        seen = set()

        while page_url:
            logger.info("Reading chapter list page %s: %s", page_no, page_url)
            soup = self.get_soup(page_url)

            if not self.novel_title:
                title = soup.select_one("h1.entry-title, h1.page-title")
                if not title:
                    raise RuntimeError("No novel title")

                self.novel_title = (
                    title.get_text(" ", strip=True)
                    .replace("Category:", "")
                    .strip()
                )
                logger.info("Novel title: %s", self.novel_title)

            links = soup.select(".all-chapters-list a")
            if not links:
                links = soup.select("article a[href*='/chapter']")

            for a in links:
                href = a.get("href")
                if not href:
                    continue

                url = self.absolute_url(href)
                if url in seen:
                    continue

                seen.add(url)

                chap_id = len(self.chapters) + 1
                vol_id = (chap_id - 1) // 100 + 1

                if len(self.volumes) < vol_id:
                    self.volumes.append(Volume(id=vol_id))

                self.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=vol_id,
                        title=a.get_text(" ", strip=True),
                        url=url,
                    )
                )

            next_link = soup.select_one("a.next.page-numbers, .nav-previous a")
            if not next_link or not next_link.get("href"):
                break

            next_url = self.absolute_url(next_link["href"]).rstrip("/") + "/"
            if next_url == page_url:
                break

            page_url = next_url
            page_no += 1

        if not self.chapters:
            raise RuntimeError("No chapters found")

        logger.info("Chapters found: %s", len(self.chapters))

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one(".entry-content")
        if not contents:
            raise RuntimeError("No chapter content")

        for bad in contents.select(
            "script, style, ins, iframe, .sharedaddy, .jp-relatedposts, "
            ".code-block, .adsbygoogle"
        ):
            bad.extract()

        return self.cleaner.extract_contents(contents)
