# -*- coding: utf-8 -*-
import logging


from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

chapter_list_url = "https://read.aixdzs.com/%s"


class AixdzsCrawler(Crawler):
    base_url = "https://www.aixdzs.com"

    def read_novel_info(self):
        if not self.novel_url.endswith("/"):
            self.novel_url += "/"
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".fdl .d_info h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_novel_cover = soup.select_one('meta[property="og:image"]')
        if possible_novel_cover:
            self.novel_cover = self.absolute_url(possible_novel_cover["content"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_novel_author = soup.select_one('meta[property="og:novel:author"]')
        if possible_novel_author:
            self.novel_author = possible_novel_author["content"]
        logger.info("%s", self.novel_author)

        # parsed_url = urlparse(self.novel_url)
        # parsed_path = parsed_url.path.strip('/').split('/')
        # chapter_url = chapter_list_url % ('/'.join(parsed_path[1:]))
        # logger.debug('Visiting %s', chapter_url)
        # soup = self.get_soup(chapter_url)

        volumes = set([])
        for a in soup.select("div.catalog li a"):
            ch_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": ch_id,
                    "volume": vol_id,
                    "title": a.text,
                    "url": self.absolute_url(a["href"]),
                }
            )

        self.volumes = [{"id": x, "title": ""} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select(".content > p")
        contents = [str(p) for p in contents if p.text.strip()]
        return "".join(contents)
