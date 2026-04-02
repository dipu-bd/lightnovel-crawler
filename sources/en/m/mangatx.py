# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressMangaTemplate


class MangaTx(WordpressMangaTemplate):
    base_url = ["https://mangatx.com/"]

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    # NOTE: Search not working, tried multiple ways just isn't showing novel.
    # def search_novel(self, query):
    #     query = query.lower().replace(" ", "+")
    #     soup = self.get_soup(self.search_url % (self.scraper.origin, query))

    #     results = []
    #     for tab in soup.select(".c-tabs-item__content"):
    #         a = tab.select_one(".post-title h3 a")
    #         latest = tab.select_one(".latest-chap .chapter a").text
    #         votes = tab.select_one(".rating .total_votes").text
    #         results.append(
    #             {
    #                 "title": a.text.strip(),
    #                 "url": self.absolute_url(a["href"]),
    #                 "info": "%s | Rating: %s" % (latest, votes),
    #             }
    #         )
    #     # end for

    #     return results
    # # end def
