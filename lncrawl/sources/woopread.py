# -*- coding: utf-8 -*-

import logging
import re

import requests
from ..utils.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = 'https://woopread.com/?s=%s&post_type=wp-manga&author=&artist=&release='

class WoopReadCrawler(Crawler):
    base_url = 'https://woopread.com/'

    def initialize(self):
        self.regex_novel_id = r'"manga_id"\s*:\s*"(?P<id>\d+)"'
    # end def

    def search_novel(self, query):
        query = query.lower().replace(' ', '+')
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select('.c-tabs-item__content'):
            a = tab.select_one('.post-title h3 a')
            latest = tab.select_one('.latest-chap .chapter a').text
            votes = tab.select_one('.rating .total_votes').text
            results.append({
                'title': a.text.strip(),
                'url': self.absolute_url(a['href']),
                'info': '%s | Rating: %s' % (latest, votes),
            })
        # end for

        return results
    # end def

    def read_novel_info(self):
        """Get novel title, autor, cover etc"""
        novel_webpage = self.get_soup(self.novel_url)
        novel_id_string = novel_webpage.find(
            text=re.compile(self.regex_novel_id))
        novel_id = re.search(self.regex_novel_id, novel_id_string).group("id")

        self.novel_title = novel_webpage.select_one(
            ".post-title h1").text.strip()
        logger.info("Novel title: %s", self.novel_title)
        self.novel_author = novel_webpage.select_one(
            ".author-content").text.strip()
        logger.info("Novel author: %s", self.novel_author)
        self.novel_cover = novel_webpage.select_one('meta[property="og:image"]')[
            "content"
        ]
        logger.info("Novel cover: %s", self.novel_title)

        volumes = set([])
        available_chapters = novel_webpage.select(
            "#manga-chapters-holder .wp-manga-chapter a"
        )
        fetch_more_chapters_html = requests.post(
            "https://woopread.com/wp-admin/admin-ajax.php",
            data={"action": "manga_get_chapters", "manga": novel_id, },
        )
        more_chapters = self.make_soup(fetch_more_chapters_html).select(
            ".wp-manga-chapter a"
        )
        all_chapters = available_chapters + more_chapters

        volumes = set([])
        for a in reversed(all_chapters):
            chap_id = len(self.chapters) + 1
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
        # end for

        self.volumes = [{"id": x, "title": ""} for x in volumes]

    # end def

    def download_chapter_body(self, chapter):
        """Download body of a single chapter and return as clean html format."""
        logger.info("Visiting %s", chapter["url"])
        chapter_page = self.get_soup(chapter["url"])

        """ TODO: ADD login option to download premium.

            Downloading of premium content has not been implemented,
            until if someone provides an active account. We return empty
            body to skip downloding these chapters.
        """
        if "This chapter is locked!" in chapter_page.text:
            return str()

        contents = chapter_page.select_one(".container .reading-content div")

        for content in contents.select("p"):
            for bad in ["Translator:", "Editor:"]:
                if bad in content.text:
                    content.decompose()

        body = self.extract_contents(contents)
        return "<p>" + "</p><p>".join(body) + "</p>"

    # end def


# end class
