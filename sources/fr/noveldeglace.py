import logging

from lncrawl.core.crawler import Crawler
from lncrawl.core.exeptions import LNException
from lncrawl.models.chapter import Chapter
from lncrawl.models.volume import Volume

logger = logging.getLogger(__name__)


class NovelDeGlace(Crawler):
    base_url = "https://noveldeglace.com/"
    last_updated = "2024-02-22"
    has_mtl = False

    def read_novel_info(self) -> None:
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        novel_details = soup.select_one("div.entry-content")
        if not novel_details:
            raise LNException("Failed to find novel details")

        for div in novel_details.find_all("div", class_="line_roman"):
            strong = div.find("strong")
            if not strong:
                continue
            strong_text = strong.text.strip()
            if strong_text == "Titre complet :":
                self.novel_title = (
                    div.text.split(":")[1].split("RSS")[0].split("CMS")[0].strip()
                )
            elif strong_text == "Auteur :":
                self.novel_author = div.text.split(":")[1].strip()

        if not self.novel_title:
            logger.debug("Failed to find novel title")

        tabs = soup.select_one("div.su-tabs-panes")
        if not tabs:
            raise LNException("Failed to find chapters")
        volume_id = 0

        rows = tabs.find_all("div", class_="su-row")

        for row in rows:

            img = row.find("img")
            if img:
                self.novel_cover = img["src"]
            else:
                logger.debug("Failed to find novel cover")

            uls = row.find_all("ul")

            if len(uls) == 0:
                raise LNException("Failed to find chapters")
            volume_span = row.find("span", class_="roman volume")

            for ul in uls:  # There is one ul for each arc
                chapters_lis = ul.find_all("li")
                for li in chapters_lis:
                    a = li.find("a")
                    if a and a.has_attr("href"):
                        self.chapters.append(
                            Chapter(
                                id=len(self.chapters) + 1,
                                title=a.text.strip(),
                                url=a["href"],
                                volume=volume_id,
                                volume_title=volume_span.text.strip(),
                            )
                        )
                    else:
                        logger.debug("Failed to find chapter link")

            self.volumes.append(Volume(id=volume_id, title=volume_span.text.strip()))
            volume_id += 1

    def download_chapter_body(self, chapter: Chapter) -> str:
        logger.debug("Visiting %s", chapter.url)
        soup = self.get_soup(chapter.url)
        body = soup.select_one("div.content-tome")
        if not body:
            body = soup.select_one("div.entry-content-chapitre")

        if body.h2:
            body.h2.decompose()
        mistape_caption = body.find("div", class_="mistape_caption")
        if mistape_caption:
            mistape_caption.decompose()
        if not body:
            raise LNException("Failed to find chapter content")

        return str(body)
