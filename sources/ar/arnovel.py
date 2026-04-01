# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler

logger = logging.getLogger(__name__)
search_url = "https://arnovel.me/?s=%s&post_type=wp-manga&author=&artist=&release="
chapter_list_url = "https://arnovel.me/wp-admin/admin-ajax.php"


class ArNovel(LegacyCrawler):
    base_url = "https://arnovel.me/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        # Add "title" to use alterntive name so you can search english name as search for arabic title doesn't work.
        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            if not a:
                continue
            title = tab.select_one(".mg_alternative .summary-content")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": title.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s" % (latest, votes),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one(".post-title h1")
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # No novel covers on site.
        # self.novel_cover = self.absolute_url(
        #     soup.select_one('.summary_image a img')['data-src'])
        # logger.info('Novel cover: %s', self.novel_cover)

        self.novel_author = " ".join([a.text.strip() for a in soup.select('.author-content a[href*="novel-author"]')])
        logger.info("%s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(self.novel_url.strip("/") + "/ajax/chapters")
        soup = self.make_soup(response)
        chapters = soup.select(".wp-manga-chapter a")
        for a in reversed(list(chapters)):
            self.chapters.append(
                Chapter(
                    id=len(self.chapters) + 1,
                    title=a.text.strip(),
                    url=self.absolute_url(a["href"]),
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select(".reading-content p")
        return "".join([str(p) for p in contents])
