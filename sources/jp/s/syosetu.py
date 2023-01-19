# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = (
    "https://yomou.syosetu.com/search.php?word=%s"
)


class SyosetuCrawler(Crawler):
    has_mtl = True
    base_url = "https://ncode.syosetu.com/"

    def search_novel(self, query):
        soup = self.get_soup(search_url % quote_plus(query))
        results = []
        for tab in soup.select(".searchkekka_box"):
            a = tab.select_one(".novel_h a")
            latest = tab.select_one(".left").get_text(separator=" ").strip()  # e.g.: 連載中 (全604部分)
            votes = tab.select_one(".attention").text.strip()  # e.g.: "総合ポイント： 625,717 pt"
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | %s" % (latest, votes),
                }
            )
        return results

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".novel_title").text.strip()

        # No novel cover.

        author_tag = soup.select_one(".novel_writername a")
        if author_tag:
            self.novel_author = author_tag.text.strip()

        # Syosetu calls parts "chapters"
        volume_id = 1
        chapter_id = 1
        for tag in soup.select(".chapter_title, .subtitle a"):
            if tag.name == "a":
                # Chapter
                self.chapters.append(
                    {
                        "id": chapter_id,
                        "volume": volume_id,
                        "url": self.absolute_url(tag["href"]),
                        "title": tag.text.strip() or ("Chapter %d" % chapter_id),
                    }
                )
                chapter_id += 1
            else:
                # Part/volume (there might be none)
                self.volumes.append(
                    {
                        "id": volume_id,
                        "title": tag.text.strip(),
                    }
                )
                volume_id += 1

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("#novel_honbun")
        return self.cleaner.extract_contents(contents)
