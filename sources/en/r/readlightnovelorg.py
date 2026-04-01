# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)
search_url = "https://www.readlightnovel.org/search/autocomplete"


class ReadLightNovelCrawler(LegacyCrawler):
    base_url = [
        "https://readlightnovel.me/",
        "https://www.readlightnovel.me/",
        "https://readlightnovel.today/",
        "https://www.readlightnovel.today/",
    ]

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".block-title h1")
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.find("img", {"alt": self.novel_title})
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_synopsis = soup.select_one(".novel-right .novel-detail-item .novel-detail-body")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        tags = soup.select(".novel-left .novel-detail-item .novel-detail-body a[href*=genre]")
        self.novel_tags = [tag.text.strip() for tag in tags if tag]
        logger.info("Novel genre: %s", self.novel_tags)

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
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip() or "Chapter %d" % chap_id,
                )
            )

        self.volumes = [Volume(id=i) for i in volume_ids]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "h3",
                "center",
                "interaction",
            ]
        )
        self.cleaner.bad_css.update(
            [
                ".trinity-player-iframe-wrapper.hidden",
                ".ads-title",
                "p.hid",
                "a[href*=remove-ads]",
                "a[target=_blank]",
                "#growfoodsmart",
                "#chapterhidden",
                'div[style*="float:left;margin-top:15px;"]',
                'div[style*="float: left; margin-top: 20px;"]',
            ]
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        div = soup.select_one(".chapter-content3 .desc")

        possible_title = div.select_one("h3")
        if possible_title:
            chapter["title"] = possible_title.text.strip()

        return self.cleaner.extract_contents(div)
