# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://meionovel.id/?s=%s&post_type=wp-manga&author=&artist=&release="


class MeionovelCrawler(Crawler):
    base_url = "https://meionovel.id/"

    # NOTE: Disabled because it takes too long
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

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"].split("-")[0]
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.select_one(".summary_image img")["data-src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        possible_authors = [a.text.strip() for a in soup.select(".author-content a")]
        self.novel_author = ", ".join(filter(None, possible_authors))
        logger.info("Novel author: %s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip("/") + "/ajax/chapters")
        soup = self.make_soup(response)
        for a in reversed(soup.select(".wp-manga-chapter a")):
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div.text-left")

        for img in contents.findAll("img"):
            if img.has_attr("data-lazy-src"):
                src_url = img["data-lazy-src"]
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        if contents.h3:
            contents.h3.extract()

        for codeblock in contents.findAll("div", {"class": "code-block"}):
            codeblock.extract()

        return str(contents)
