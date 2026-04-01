# -*- coding: utf-8 -*-
import logging
from urllib.parse import quote_plus

from lncrawl.core import Chapter, PageSoup, Volume
from lncrawl.templates.browser.basic import BasicBrowserTemplate

logger = logging.getLogger(__name__)
search_url = "https://syosetu.org/search/?mode=search&word=%s"


class SyosetuOrgCrawler(BasicBrowserTemplate):
    has_mtl = True
    base_url = "https://syosetu.org/"

    def initialize(self) -> None:
        self.init_executor(2)

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

    def read_novel_info_in_soup(self):
        """Read novel info using regular scraper"""
        soup = self.get_soup(self.novel_url)
        self._parse_novel_info(soup)

    def read_novel_info_in_browser(self):
        """Read novel info using browser"""
        self.visit(self.novel_url)
        soup = self.browser.soup
        self._parse_novel_info(soup)

    def _parse_novel_info(self, soup: PageSoup):
        """Common logic for parsing novel info"""
        title_tag = soup.select_one("span[itemprop='name']")
        if title_tag:
            self.novel_title = title_tag.text.strip()
        else:
            self.novel_title = soup.select_one("title").text.split(" - ")[0].strip()
        logger.debug("Novel title: %s", self.novel_title)

        # No novel cover.

        author_tag = soup.select_one("span[itemprop='author'] a")
        if author_tag:
            self.novel_author = author_tag.text.strip()

        # Syosetu.org chapters are in a table
        volume_id = 1
        chapter_id = 0
        self.volumes.append(Volume(id=1))

        table = soup.select_one("table")
        if table:
            rows = table.select("tr")
            for row in rows:
                tds = row.select("td")
                if len(tds) == 1 and tds[0].get("colspan") == "2":
                    # Volume header
                    strong = tds[0].select_one("strong")
                    if strong:
                        volume_id += 1
                        self.volumes.append(
                            Volume(
                                id=volume_id,
                                title=strong.text.strip(),
                            )
                        )
                elif len(tds) == 2:
                    # Chapter row
                    a_tag = tds[0].select_one("a")
                    if a_tag and "href" in a_tag.attrs:
                        chapter_id += 1
                        self.chapters.append(
                            Chapter(
                                id=chapter_id,
                                volume=volume_id,
                                title=a_tag.text.strip(),
                                url=self.absolute_url(a_tag["href"]),
                            )
                        )

    def download_chapter_body_in_soup(self, chapter):
        """Download chapter content using regular scraper"""
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("#honbun")
        return self.cleaner.extract_contents(contents)

    def download_chapter_body_in_browser(self, chapter):
        """Download chapter content using browser"""
        self.visit(chapter["url"])
        soup = self.browser.soup
        contents = soup.select_one("#honbun")
        return self.cleaner.extract_contents(contents)
