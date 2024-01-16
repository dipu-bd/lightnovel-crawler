# -*- coding: utf-8 -*-
import logging
import re

from bs4.element import Tag
from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter, SearchResult

logger = logging.getLogger(__name__)


class TigerTranslations(Crawler):
    base_url = "https://tigertranslations.org/"

    # there's certain text within the .the-content which can be removed
    removable_texts = ["Page 1", "Page 2", "Next Chapter", "Previous Chapter"]

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        content = soup.select_one("div.the-content")

        entry_title = soup.select_one("h1.entry-title")
        assert isinstance(entry_title, Tag)  # this must be here, is part of normal site structure/framework
        self.novel_title = entry_title.text
        self.novel_author = "TigerTranslations"

        for line in content.text.splitlines():
            if "author:" in line.lower():
                self.novel_author = line[line.find(':') + 1:].strip()
                # Use synopsis to refer to translator / source -> not sure if ok to do
                self.novel_synopsis = "Translated by TigerTranslations.org"
                break  # no need to continue after finding author

        logger.info("Novel title: %s", self.novel_title)
        logger.info("Novel author: %s", self.novel_author)

        # image may or may not be wrapped (in a p) in a span element
        image_locations = ['div.the-content > img',
                           'div.the-content > span > img',
                           'div.the-content > p > span > img']

        for location in image_locations:
            possible_cover = soup.select_one(location)
            if isinstance(possible_cover, Tag):
                self.novel_cover = self.absolute_url(possible_cover["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        for a in soup.select("div.the-content > p > a"):
            # The selector gets all chapters but also a donation link
            if not a.text.strip().lower().startswith("chapter"):
                continue
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            if chap_id % 100 == 1:
                self.volumes.append(
                    Volume(
                        id=vol_id,
                        title=vol_title
                    ))

            # chapter name is only present in chapter page, not in overview
            # this workaround makes titles "Chapter-x"
            entry_title = a.text

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=self.absolute_url(a["href"]),
                    title=entry_title,
                    volume=vol_id,
                    volume_title=vol_title
                ),
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter.url)

        # try to figure out if there is a 2nd page or not, try different possible links
        # example: https://tigertranslations.org/2018/09/16/jack-of-all-trades-7/
        info = re.fullmatch("(https://tigertranslations\\.org)/(\\d+/\\d+/\\d+)/(.+)/?", chapter.url)
        domain, publish_date, chap_uri = info.groups()
        page2 = f"{domain}/{publish_date}/{chap_uri}-2"
        page2_alt = f"{domain}/{chap_uri}"
        soup2 = None
        try:
            soup2 = self.get_soup(page2)
        except Exception:
            try:
                soup2 = self.get_soup(page2_alt)
            except Exception:
                pass
        # We need to clean the HTML first due to obsessive amounts of newlines
        # also if soup2 (aka a 2nd page) exists, it's processed & appended.
        contents_html = soup.select_one("div.the-content")
        contents_html = self.cleaner.clean_contents(contents_html)
        contents_str = self.cleaner.extract_contents(contents_html)
        # There's a novel title wrapped in tags at the end, we remove it here
        # in a way that likely won't remove it from "real" chapter text. Example Input:
        # ...this is chapter text.</p><p>PAGE 2</p><p>Jack of all Trades</p>
        novel_title = re.search(f"(<p>{self.novel_title}</p>)", contents_str, re.IGNORECASE).group()
        if novel_title:
            logger.info("Removing novel title at end of chapter like this: %s", novel_title)
            contents_str = contents_str.replace(novel_title, '')

        if soup2 is not None:
            contents_html = soup2.select_one("div.the-content")
            contents_html = self.cleaner.clean_contents(contents_html)
            contents_str += self.cleaner.extract_contents(contents_html)

        # remove annoyances (such as "Page 2")
        for text in self.removable_texts:
            contents_str = contents_str.replace(text, '')
            contents_str = contents_str.replace(text.upper(), '')
            contents_str = contents_str.replace(text.lower(), '')

        return contents_str

    def search_novel(self, query: str):
        soup = self.get_soup("https://tigertranslations.org/")
        novels = soup.select("ul.menu-wrap > li > a")
        results = []

        for novel in novels:
            # simple but at least won't taint results
            if query.lower() in novel.text.lower():
                results.append(
                    SearchResult(
                        title=novel.text,
                        url=novel["href"]
                    )
                )

        return results
