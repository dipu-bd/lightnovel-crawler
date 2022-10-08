# -*- coding: utf-8 -*-
import logging

import js2py
from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RanobeLibCrawler(Crawler):
    base_url = [
        "http://ranobes.net/",
        "https://ranobes.net/",
    ]

    def initialize(self) -> None:
        self.init_executor(1)
        self.cleaner.bad_css.update([".free-support", 'div[id^="adfox_"]'])

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        main_page_link = soup.select_one("#mainside, .breadcrumbs-panel")
        if isinstance(main_page_link, Tag):
            main_page_link = main_page_link.select_one('a[href*="/novels/"]')
            if isinstance(main_page_link, Tag):
                self.novel_url = self.absolute_url(main_page_link["href"])
                logger.info("Visiting %s", self.novel_url)
                soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert isinstance(possible_title, Tag)
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one('meta[property="og:image"]')
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        author_link = soup.select_one('.tag_list a[href*="/authors/"]')
        if isinstance(author_link, Tag):
            self.novel_author = author_link.text.strip().title()
        logger.info("Novel author: %s", self.novel_author)

        chapter_list_link = soup.select_one(
            '#fs-chapters a[title="Go to table of contents"]'
        )
        assert isinstance(chapter_list_link, Tag)
        chapter_list_link = self.absolute_url(chapter_list_link["href"])

        logger.info("Visiting %s", chapter_list_link)
        soup = self.get_soup(chapter_list_link)

        script = soup.find(
            lambda tag: isinstance(tag, Tag)
            and tag.name == "script"
            and tag.text.startswith("window.__DATA__")
        )
        assert isinstance(script, Tag)

        data = js2py.eval_js(script.text).to_dict()
        assert isinstance(data, dict)

        pages_count = data["pages_count"]
        logger.info("Total pages: %d", pages_count)

        futures = []
        page_soups = [soup]
        for i in range(2, pages_count + 1):
            chapter_page_url = chapter_list_link.strip("/") + ("/page/%d" % i)
            f = self.executor.submit(self.get_soup, chapter_page_url)
            futures.append(f)
        page_soups += [f.result() for f in futures]

        volumes = set([])
        for soup in reversed(page_soups):
            script = soup.find(
                lambda tag: isinstance(tag, Tag)
                and tag.name == "script"
                and tag.text.startswith("window.__DATA__")
            )
            assert isinstance(script, Tag)

            data = js2py.eval_js(script.text).to_dict()
            assert isinstance(data, dict)

            for chapter in reversed(data["chapters"]):
                chap_id = len(self.chapters) + 1
                vol_id = len(self.chapters) // 100 + 1
                volumes.add(vol_id)
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": vol_id,
                        "title": chapter["title"],
                        "url": "https://ranobes.net/read-%s.html" % chapter["id"],
                    }
                )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        article = soup.select_one('.text[itemprop="description"]')
        self.cleaner.clean_contents(article)
        return str(article)
