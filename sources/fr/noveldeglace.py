import logging
from typing import List, Set

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models.chapter import Chapter
from lncrawl.models.volume import Volume

logger = logging.getLogger(__name__)

# TODO: Skip links that only link to parts of the same chapter
# TODO: Check if images work

class NovelDeGlace(Crawler):
    base_url = "https://noveldeglace.com/"
    last_updated = "2024-02-21"
    has_mtl = False
    # https://noveldeglace.com/roman/genjitsushugisha-no-oukokukaizouki/
    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)
        
        # novel details under su-column-inner su-clearfix
        novel_details = soup.select_one("div.su-column-inner.su-clearfix")
        if not novel_details:
            raise LNException("Failed to find novel details")

        # Now look through all the divs with class line_roman
        for div in novel_details.find_all("div", class_="line_roman"):
            # get the strong tag
            strong = div.find("strong")
            if not strong:
                continue
            # get the text of the strong tag
            strong_text = strong.text.strip()
            # Get title and cover
            if strong_text == "Titre complet :":
                self.novel_title = div.text.split(":")[1].strip()
            elif strong_text == "Auteur :":
                self.novel_author = div.text.split(":")[1].strip()

        # get su-tabs-panes div
        tabs = soup.select_one("div.su-tabs-panes")
        if not tabs:
            raise LNException("Failed to find chapters")
        volume_id = 1
        # get all divs with class su-row. these all contain one tome
        rows = tabs.find_all("div", class_="su-row")
        for row in rows:
            # get the first img
            img = row.find("img")
            if img:
                self.novel_cover = img["src"]
            else:
                logger.debug("Failed to find novel cover")
            volume = row.find("span", class_="roman volume")
            if volume:
                volume_title = volume.text.strip()
                self.volumes.append(Volume(id=volume_id, title=volume_title))
            else:
                logger.debug("Failed to find volume title")
                self.volumes.append(Volume(id=volume_id, title=f"Tome {volume_id}"))
            volume_id += 1

            # get the next ul
            ul = row.find("ul")
            if not ul:
                raise LNException("Failed to find chapters")
            # get all li elements
            chapters_lis = ul.find_all("li")
            # for each chapter, get the first link
            for li in chapters_lis:
                a = li.find("a")
                if a:
                    self.chapters.append(
                        Chapter(
                            id=len(self.chapters) + 1, title=a.text.strip(), url=a["href"], volume=volume_id
                        )
                    )
                else:
                    logger.debug("Failed to find chapter link")

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
