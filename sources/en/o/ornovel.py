# -*- coding: utf-8 -*-
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class OrNovel(Crawler):
    base_url = "https://www.ornovel.com/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = " ".join(
            [str(x) for x in soup.select_one(".title h1").contents if not x.name]
        ).strip()
        logger.info("Novel title: %s", self.novel_title)

        probable_img = soup.select_one(".intro-left img.book-image")
        if probable_img:
            self.novel_cover = self.absolute_url(probable_img["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [a.text.strip() for a in soup.select(".author-container")]
        )
        logger.info("%s", self.novel_author)

        volumes = set()
        chapters = soup.select("ul.chapters-all li.chapters-item a")
        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.chapter-detail")
        for bad in contents.select(
            "h2, ins, .chapter-header .code-block, script, .adsbygoogle"
        ):
            bad.extract()

        return str(contents)
