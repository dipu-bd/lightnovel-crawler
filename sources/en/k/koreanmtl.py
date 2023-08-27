# -*- coding: utf-8 -*-
import re
import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class LightNovelsOnl(Crawler):
    has_mtl = True
    base_url = "https://www.koreanmtl.online/"

    def initialize(self) -> None:
        self.init_parser("html5lib")

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        # self.novel_title = soup.select_one('h1.entry-title').text.strip()
        possible_title = soup.select_one(".post-title.entry-title")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        volumes = set([])
        for a in soup.select(".post-body.entry-content ul li a"):
            chap_id = 1 + len(self.chapters)
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".post-body.entry-content")
        for el in contents.select('div[style="text-align:center;"]'):
            el.extract()
        body = ""
        for p in contents.select("p"):
            line = p.text.strip()
            line = re.sub(r"<", "&lt;", line)
            line = re.sub(r">", "&gt;", line)
            line = re.sub(r"\u3008", "&lt;", line)
            line = re.sub(r"\u3009", "&gt;", line)
            line = re.sub(r"\uff08", "(", line)
            line = re.sub(r"\uff09", ")", line)
            line = re.sub(r"\uff0c", ",", line)
            line = re.sub(r"\u2026", "...", line)
            line = re.sub(r"\uff1e", "&gt;", line)
            line = re.sub(r"\u200b", "  ", line)
            line = re.sub(r"\u3001", "`", line)
            line = re.sub(r"(\(\))|(\[\])", "", line)
            # line = re.sub(r'([\u00FF-\uFFFF])', lambda m: '&#x%d;' % ord(m.group(1)), line)
            if re.search(r"[\w\d]", line):
                body += "<p>" + line + "</p>"
        return body
