# -*- coding: utf-8 -*-
import logging
from bs4.element import Tag


from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.neosekaitranslations.com/?s=%s&post_type=wp-manga"
chapter_list_url = "https://www.neosekaitranslations.com/wp-admin/admin-ajax.php"


class NeoSekaiCrawler(Crawler):
    base_url = "https://www.neosekaitranslations.com/"

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            if not isinstance(a, Tag):
                continue
            latest = tab.select_one(".latest-chap .chapter a")
            if isinstance(latest, Tag):
                latest = latest.text.strip()
            status = tab.select_one(".mg_release .summary-content a")
            if isinstance(status, Tag):
                status = "Status: " + status.text.strip()
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": " | ".join(filter(None, [latest, status])),
                }
            )
        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one('meta[property="og:title"]')
        assert possible_title, "No novel title"
        self.novel_title = possible_title["content"]
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one(".summary_image a img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join(
            [
                a.text.strip()
                for a in soup.select('.author-content a[href*="novel-author"]')
            ]
        )
        logger.info("%s", self.novel_author)

        self.novel_id = soup.select_one("#manga-chapters-holder")["data-id"]
        logger.info("Novel id: %s", self.novel_id)

        response = self.submit_form(
            chapter_list_url, data="action=manga_get_chapters&manga=" + self.novel_id
        )
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
        contents = soup.select_one(".reading-content")
        # all_imgs = soup.find_all('img')
        # for img in all_imgs:
        #     if img.has_attr('loading'):
        #         src_url = img['src']
        #         parent = img.parent
        #         img.extract()
        #         new_tag = soup.new_tag("img", src=src_url)
        #         parent.append(new_tag)
        return self.cleaner.extract_contents(contents)
