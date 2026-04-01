# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)


class AnythingNovelCrawler(LegacyCrawler):
    base_url = "https://anythingnovel.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.select("#wrap .breadcrumbs span")[-1].text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one("#content a img")
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        volumes = set([])
        for a in reversed(soup.select("#content div li a")):
            title = a.text.strip()
            chapter_id = len(self.chapters) + 1
            volume_id = 1 + (chapter_id - 1) // 100
            volumes.add(volume_id)
            self.chapters.append(
                Chapter(
                    id=chapter_id,
                    volume=volume_id,
                    title=title,
                    url=a["href"],
                )
            )

        self.chapters.sort(key=lambda x: x["id"])
        self.volumes = [Volume(id=x) for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.select_one("div#content")
        self.cleaner.clean_contents(content)
        paragraphs = [str(p) for p in content.select("p") if p.text and p.text.lower() != "advertisement"]
        return "<p>" + "</p><p>".join(paragraphs) + "</p>"

    def should_take(self, p):
        txt = p.text.strip().lower()
        return txt and txt != "advertisement"
