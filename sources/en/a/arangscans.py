# -*- coding: utf-8 -*-
from lncrawl.templates.wordpress import WordpressTemplate


class ArangScans(WordpressTemplate):
    base_url = 'https://arangscans.com/'
    chapter_body_selector = "div.text-left"

    def initialize(self) -> None:
        self.cleaner.bad_css.update(["h3"])

    # FIXME: Can't seem to get search to work not showing up when running command "lncrawl -q "Rooftop Sword Master" --sources"
    # def search_novel(self, query):
    #     query = query.lower().replace(' ', '+')
    #     soup = self.get_soup(search_url % query)

    #     results = []
    #     for tab in soup.select('.c-tabs-item__content'):
    #         a = tab.select_one('.post-title h3 a')
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
