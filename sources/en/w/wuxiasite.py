# -*- coding: utf-8 -*-
import logging

from bs4.element import Tag

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://wuxiaworld.site/?s=%s&post_type=wp-manga"


class WuxiaSiteCrawler(Crawler):
    base_url = "https://wuxiaworld.site/"

    # NOTE: Disabled due to Cloudflare issue.
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('.c-tabs-item__content'):
    #         a = tab.select_one('.post-title h4 a')
    #         latest = tab.select_one('.latest-chap .chapter a').text
    #         votes = tab.select_one('.rating .total_votes').text
    #         results.append({
    #             'title': a.text.strip(),
    #             'url': self.absolute_url(a['href']),
    #             'info': '%s | Rating: %s' % (latest, votes),
    #         })
    #     # end for

    #     return results
    # # end def

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title")
        assert isinstance(possible_title, Tag)
        possible_title = possible_title.select_one("h1, h2, h3")
        assert isinstance(possible_title, Tag)
        self.novel_title = " ".join(
            [str(x) for x in possible_title.contents if not isinstance(x, Tag)]
        ).strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image a img")
        if isinstance(possible_image, Tag):
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        authors = soup.select(".author-content a")
        if len(authors) == 2:
            self.novel_author = authors[0].text + " (" + authors[1].text + ")"
        elif len(authors) == 1:
            self.novel_author = authors[0].text
        logger.info("Novel author: %s", self.novel_author)

        possible_chapter = soup.select_one(".page-content-listing .wp-manga-chapter a")
        assert isinstance(possible_chapter, Tag)
        chapter_link = self.absolute_url(possible_chapter["href"])
        logger.info("chapter: %s", chapter_link)
        soup = self.get_soup(chapter_link)

        for option in reversed(soup.select("select.selectpicker_chapter option")):
            chap_id = len(self.chapters) + 1
            vol_id = len(self.chapters) // 100 + 1
            if len(self.chapters) % 100 == 0:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": option.text.strip(),
                    "url": self.absolute_url(option["data-redirect"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        content = soup.select_one(".text-left")
        if not isinstance(content, Tag):
            content = soup.select_one(".cha-words")
        if not isinstance(content, Tag):
            content = soup.select_one(".reading-content")

        return self.cleaner.extract_contents(content)
