# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.readlightnovel.org/search/autocomplete"


class ReadLightNovelCrawler(Crawler):
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
        assert isinstance(possible_title, Tag), "Novel title is not found"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.find("img", {"alt": self.novel_title})
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_synopsis = soup.select_one(
            ".novel-right .novel-detail-item .novel-detail-body"
        )
        if isinstance(possible_synopsis, Tag):
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        tags = soup.select(
            ".novel-left .novel-detail-item .novel-detail-body a[href*=genre]"
        )
        self.novel_tags = [tag.text.strip() for tag in tags if isinstance(tag, Tag)]
        logger.info("Novel genre: %s", self.novel_tags)

        author_link = soup.select_one("a[href*=author]")
        if isinstance(author_link, Tag):
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
                ".trinity-player-iframe-wrapper" ".hidden",
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
        assert isinstance(div, Tag)

        possible_title = div.select_one("h3")
        if isinstance(possible_title, Tag):
            chapter["title"] = possible_title.text.strip()

        return self.cleaner.extract_contents(div)
