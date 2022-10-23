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

        possible_title = soup.select_one("h1.entry-title")
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        # image may or may not be wrapped (in a p) in a span element
        image_locations = ['div.the-content > img',
                           'div.the-content > span > img',
                           'div.the-content > p > span > img']

        for location in image_locations:
            possible_image = soup.select_one(location)
            if isinstance(possible_image, Tag):
                self.novel_cover = self.absolute_url(possible_image["src"])

        logger.info("Novel cover: %s", self.novel_cover)

        # Author is located at a different place each time in a "random"
        # <p> tag, can't really consistently access it
        self.novel_author = "Unknown"
        logger.info("Novel author: %s", self.novel_author)

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
            title = a.text

            self.chapters.append(
                Chapter(
                    id=chap_id,
                    url=self.absolute_url(a["href"]),
                    title=title,
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
        if soup2 is not None:
            contents_html = soup2.select_one("div.the-content")
            contents_html = self.cleaner.clean_contents(contents_html)
            contents_str += self.cleaner.extract_contents(contents_html)

        # remove annoyances (such as "Page 2")
        for text in self.removable_texts:
            contents_str = contents_str.replace(text, '')
            contents_str = contents_str.replace(text.upper(), '')
            contents_str = contents_str.replace(text.lower(), '')
            # because the novel's name is usually appended every 2nd page
            # it's also manually removed
            novel_name = ' '.join([p.capitalize() for p in chap_uri.split('-')][:-1])
            contents_str = contents_str.replace(novel_name, '')

        return contents_str

    def search_novel(self, query: str):
        soup = self.get_soup("https://tigertranslations.org/")
        novels = soup.select("ul.menu-wrap > li > a")
        results = []

        for novel in novels:
            results.append(
                SearchResult(
                    title=novel.text,
                    url=novel["href"]
                )
            )

        return results
