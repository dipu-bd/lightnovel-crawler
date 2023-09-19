# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://yomou.syosetu.com/search.php?word=%s"


class SyosetuCrawler(Crawler):
    has_mtl = True
    base_url = "https://ncode.syosetu.com/"

    def search_novel(self, query):
        soup = self.get_soup(search_url % quote_plus(query))
        results = []
        for tab in soup.select(".searchkekka_box"):
            a = tab.select_one(".novel_h a")
            latest = (
                tab.select_one(".left").get_text(separator=" ").strip()
            )  # e.g.: 連載中 (全604部分)
            votes = tab.select_one(
                ".attention"
            ).text.strip()  # e.g.: "総合ポイント： 625,717 pt"
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | %s" % (latest, votes),
                }
            )
        return results

    def read_novel_info(self):
        self.init_parser('xml')
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one(".novel_title").text.strip()
        logger.debug('Novel title: %s', self.novel_title)

        # No novel cover.

        author_tag = soup.select_one(".novel_writername a")
        if author_tag:
            self.novel_author = author_tag.text.strip()

        # Syosetu calls parts "chapters"
        chapter_id = 0
        volume = {"id": 0}
        self.volumes.append(volume)
        for tag in soup.select(".index_box .chapter_title, .index_box .subtitle a"):
            if 'chapter_title' in tag.attrs.get('class', ''):
                # Part/volume (there might be none)
                volume = {
                    "id": volume['id'] + 1,
                    "title": tag.text.strip(),
                }
                self.volumes.append(volume)
            elif tag.name == "a":
                # Chapter
                chapter_id += 1
                self.chapters.append(
                    {
                        "id": chapter_id,
                        "volume": volume['id'],
                        "title": tag.text.strip() or ("Chapter %d" % chapter_id),
                        "url": self.absolute_url(tag["href"]),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("#novel_honbun")
        contents = self.cleaner.extract_contents(contents)
        return contents
