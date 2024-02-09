# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag
from lncrawl.core.crawler import Crawler
from lncrawl.models import Volume, Chapter, SearchResult

logger = logging.getLogger(__name__)


class FaqWiki(Crawler):
    base_url = ["https://faqwiki.us/"]
    has_manga = False
    has_mtl = True

    def initialize(self) -> None:
        # There's about 4+ ads as img tags within each chapter.
        # Have not yet seen an img be part of any chapter, worst case we'll miss out on it.
        self.cleaner.bad_tags.add("img")

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        content = soup.select_one(".entry-content")

        entry_title = soup.select_one("h1.entry-title")
        assert isinstance(entry_title, Tag)  # this must be here, is part of normal site structure/framework
        self.novel_title = entry_title.text.strip()
        # remove suffix from completed novels' title
        if self.novel_title.endswith(" – All Chapters"):
            self.novel_title = self.novel_title[0:self.novel_title.find(" – All Chapters")]
        self.novel_author = "FaqWiki"
        cover = content.select_one('.wp-block-image img')
        # is missing in some rarer cases
        if cover:
            src = str(cover['src'])
            # may be replaced with JS after load, in such case try and get the real img hidden in data-values
            if src.startswith("data:"):
                try:
                    src = cover["data-ezsrc"]
                except KeyError:
                    pass
            self.novel_cover = self.absolute_url(src)
        # remove any optimized image size GET args from novel cover URL
        if self.novel_cover and "?" in self.novel_cover:
            self.novel_cover = self.novel_cover[0:self.novel_cover.find("?")]

        metadata_container = soup.select_one("div.book-review-block__meta-item-value")
        keywords = {
            "desc": "Description:",
            "alt_name": "Alternate Names:",
            "genre": "Genre:",
            "author": "Author(s):",
            "status": "Status:",
            "original_pub": "Original Publisher:"
        }

        if metadata_container:
            metadata = metadata_container.text  # doesn't have line breaks anyway so not splitting here
            pos_dict = {}
            for key, sep in keywords.items():
                pos_dict[key + "_start"] = metadata.find(sep)
                pos_dict[key] = metadata.find(sep) + len(sep)

            self.novel_synopsis = metadata[pos_dict["desc"]:pos_dict["alt_name_start"]].strip()
            self.novel_tags = metadata[pos_dict["genre"]:pos_dict["author_start"]].strip().split(" ")
            self.novel_author = metadata[pos_dict["author"]:pos_dict["status_start"]].strip()

        logger.info("Novel title: %s", self.novel_title)
        logger.info("Novel synopsis: %s", self.novel_synopsis)
        logger.info("Novel tags: %s", ",".join(self.novel_tags))
        logger.info("Novel author: %s", self.novel_author)
        logger.info("Novel cover: %s", self.novel_cover)

        chap_list = soup.select_one('#lcp_instance_0').select("li>a")

        for idx, a in enumerate(chap_list):
            if "chapter" not in a.text.lower():
                continue
            chap_id = 1 + idx
            vol_id = 1 + len(self.chapters) // 100
            vol_title = f"Volume {vol_id}"
            if chap_id % 100 == 1:
                self.volumes.append(
                    Volume(
                        id=vol_id,
                        title=vol_title
                    ))

            # chapter name is only (sometimes) present in chapter page, not in overview
            entry_title = f"Chapter {chap_id}"

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

        contents_html = soup.select_one("div.entry-content")
        contents_html = self.cleaner.clean_contents(contents_html)
        contents_str = self.cleaner.extract_contents(contents_html)

        return contents_str

    def search_novel(self, query: str):
        novel_selector = "article > div > header > h3.entry-title > a"
        next_selector = "div.nav-links > a.next"

        soup = self.get_soup(f"https://faqwiki.us/?s={query.replace(' ','+')}&post_type=page")
        empty = "nothing found" in soup.select_one("h1.page-title").text.strip().lower()
        if empty:
            return []

        novels = soup.select(novel_selector)

        # loop over all pages via next button and get all novels
        next_page = soup.select_one(next_selector)
        while next_page:
            page_soup = self.get_soup(self.absolute_url(next_page["href"]))
            novels += page_soup.select(novel_selector)
            next_page = page_soup.select_one(next_selector)

        results = []
        for novel in novels:
            # filter out "fake" novels (links to All, completed & ongoing pages)
            if "novels" in novel.text.lower():
                pass
            # simple but at least won't taint results
            if query.lower() in novel.text.lower():
                results.append(
                    SearchResult(
                        title=novel.text,
                        url=novel["href"]
                    )
                )
        return results
