# -*- coding: utf-8 -*-
import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://novelsonline.net/search/autocomplete"


class NovelsOnline(Crawler):
    base_url = "https://novelsonline.net/"

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".block-title h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find("img", {"alt": self.novel_title})["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        author_link = soup.select_one("a[href*=author]")
        if author_link:
            self.novel_author = author_link.text.strip().title()
        logger.info("Novel author: %s", self.novel_author)

        volume_ids = set()
        for a in soup.select(".chapters .chapter-chs li a"):
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volume_ids.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": i} for i in volume_ids]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        div = soup.select_one(".chapter-content3")

        bad_selectors = [
            ".trinity-player-iframe-wrapper" ".hidden",
            ".ads-title",
            "script",
            "center",
            "interaction",
            "a[href*=remove-ads]",
            "a[target=_blank]",
            "hr",
            "br",
            "#growfoodsmart",
            ".col-md-6",
        ]
        for hidden in div.select(", ".join(bad_selectors)):
            hidden.extract()

        body = self.cleaner.extract_contents(div)
        if re.search(r"c?hapter .?\d+", body[0], re.IGNORECASE):
            title = body[0].replace("<strong>", "").replace("</strong>", "").strip()
            title = ("C" if title.startswith("hapter") else "") + title
            chapter["title"] = title.strip()
            body = body[1:]

        return "<p>" + "</p><p>".join(body) + "</p>"
