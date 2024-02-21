import logging
from typing import List, Set

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models.chapter import Chapter
from lncrawl.models.volume import Volume

logger = logging.getLogger(__name__)

# TODO: Skip links that only link to parts of the same chapter
class NovelDeGlace(Crawler):
    base_url = "https://noveldeglace.com/"
    last_updated = "2024-02-21"
    has_mtl = False
    # https://noveldeglace.com/roman/genjitsushugisha-no-oukokukaizouki/
    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)
        # get su-tabs-panes div
        tabs = soup.select_one("div.su-tabs-panes")
        if not tabs:
            raise LNException("Failed to find chapters")
        links = tabs.find_all("a", href=True)
        processed_urls: Set[str] = set()
        processed_volumes: Set[int] = set()
        for link in links:
            href = link["href"]
            if href.startswith("https://noveldeglace.com/chapitre/"):
                if href in processed_urls:
                    continue
                else:
                    # search for the string "tome-<nr>" in the href
                    tome = int(href.split("tome-")[1].split("-")[0])
                    if tome not in processed_volumes:
                        # TODO: Get proper title
                        self.volumes.append(Volume(id=tome, title=f"Tome {tome}"))
                        processed_volumes.add(tome)
                    self.chapters.append(
                        Chapter(
                            id=len(self.chapters) + 1, title=link.text.strip(), url=href, volume=tome
                        )
                    )
                    processed_urls.add(href)

        # Log all chapters
        logger.debug("%s", self.chapters)

    def download_chapter_body(self, chapter: Chapter) -> str:
        logger.debug("Visiting %s", chapter.url)
        soup = self.get_soup(chapter.url)
        # get div with entry-content-chapitre 
        body = soup.select_one("div.entry-content-chapitre")
        if not body:
            raise LNException("Failed to find chapter content")
        return str(body)
