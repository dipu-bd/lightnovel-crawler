# -*- coding: utf-8 -*-
import logging
import re
import requests
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class FenrirScans(Crawler):
    base_url = ["https://fenrirscans.com/"]
    search_url = "https://fenrirscans.com/wp-admin/admin-ajax.php"
    has_manga = False
    has_mtl = False

    def search_novel(self, query):
        """
        Uses the site's AJAX search endpoint to find novels.
        """
        # Prepare payload for AJAX search
        data = {
            "action": "ts_ac_do_search",
            "ts_ac_query": query,
        }
        response = requests.post(self.search_url, data=data)
        novels = []
        try:
            results = response.json().get("series", [])[0].get("all", [])
        except Exception:
            return novels
        for item in results:
            title = item.get("post_title")
            url = item.get("post_link")
            if title and url:
                novels.append(
                    {
                        "title": title,
                        "url": self.absolute_url(url),
                    }
                )
        return novels

    def read_novel_info(self):
        """
        Parses novel metadata and chapter list from the novel page.
        """
        soup = self.get_soup(self.novel_url)
        # Metadata
        title = soup.find("h1")
        if title:
            self.novel_title = title.text.strip()

        # Synopsis
        summary = soup.find("div", {"class": "entry-content"})
        if summary:
            self.novel_synopsis = self.cleaner.extract_contents(summary)

        # Cover
        cover = soup.find("img", {"class": "wp-post-image"})
        if cover:
            self.novel_cover = self.absolute_url(cover.get("src"))
        # Tags/Genres
        for tag in soup.select('a[rel="tag"]'):
            self.novel_tags.append(tag.text)

        # Author
        author = soup.find("a", href=re.compile(r"/authors/"))
        if author:
            self.novel_author = author.text.strip()

        # Chapters
        chapter_links = soup.find_all("a", href=re.compile(r"-bolum-\d+"))
        # Reverse so earliest chapters first
        chapter_links = list(reversed(chapter_links))
        for idx, a in enumerate(chapter_links, 1):
            chap_url = self.absolute_url(a["href"])
            chap_title = a.find("span", {"class": "chapternum"})
            if chap_title:
                chap_title = chap_title.text.strip()
            else:
                chap_title = a.text.strip()
            self.chapters.append(
                {
                    "id": idx,
                    "volume": 1,
                    "url": chap_url,
                    "title": chap_title,
                }
            )

    def download_chapter_body(self, chapter):
        """
        Downloads the body of a single chapter.
        """
        soup = self.get_soup(chapter["url"])
        content = soup.find("div", {"id": "readerarea"})
        if not content:
            logger.error("No content found for chapter: %s", chapter["url"])
            return None
        return self.cleaner.extract_contents(content)
