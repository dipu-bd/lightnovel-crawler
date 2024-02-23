# -*- coding: utf-8 -*-
import json
import logging
from bs4 import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Reaperscans(Crawler):
    base_url = "https://reaperscans.com/"

    def initialize(self):
        self.cleaner.bad_text_regex = set(
            [
                "Translator",
                "Proofreader",
                "Reaper Scans",
                "REAPER SCANS",
                "https://dsc.gg/reapercomics",
                "https://discord.gg/MaRegMFhRb",
                "https://discord.gg/reapercomics",
                "h ttps://discord.gg/reapercomic",
                "https://discord.gg/sb2jqkv",
                "____",
                "Join our Discord",
            ]
        )
        self.init_executor(ratelimit=0.9)

    def get_chapters_from_page(self, page, body):
        url = self.absolute_url("/livewire/message/" + body["fingerprint"]["name"])
        body["updates"] = [
            {
                "type": "callMethod",
                "payload": {
                    "id": "00000",
                    "method": "gotoPage",
                    "params": [page, "page"],
                },
            }
        ]

        response = self.post_json(url=url, data=json.dumps(body), timeout=10)
        return self.make_soup(response["effects"]["html"])

    def get_chapters_from_doc(self, dom):
        return [
            {
                "title": a.select_one("p").text.strip(),
                "url": self.absolute_url(a["href"]),
            }
            for a in dom.select("div[wire\\3A id] ul[role] li a")
        ]

    def insert_chapters(self, chapters):
        self.chapters = [
            {
                "id": i + 1,
                "title": x["title"],
                "url": x["url"],
            }
            for i, x in enumerate(reversed(chapters))
        ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select_one("h1").text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".h-full .w-full img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        # livewire container
        container = soup.select_one("main div[wire\\:id][wire\\:initial-data]")
        # first page ssr json
        body = json.loads(container["wire:initial-data"])
        body.pop("effects")
        # initial chapters from soup
        chapters = self.get_chapters_from_doc(container)
        page_count = 1
        last_page = container.select_one(
            'span[wire\\:key^="paginator-page"]:nth-last-child(2)'
        )

        if isinstance(last_page, Tag):
            page_count = int(last_page.text.strip())
        else:
            self.insert_chapters(chapters)
            # if we don't have the pagination el
            return

        toc_futures = [
            self.executor.submit(self.get_chapters_from_page, k, body)
            for k in range(2, page_count + 1)
        ]
        self.resolve_futures(toc_futures, desc="TOC", unit="page")
        for f in toc_futures:
            chapters.extend(self.get_chapters_from_doc(f.result()))

        self.insert_chapters(chapters)

    def download_chapter_body(self, chapter):
        # TODO: better retry/timeout settings
        soup = self.get_soup(chapter["url"], retry=3, timeout=10)
        contents = soup.select_one("article")
        return self.cleaner.extract_contents(contents)
