# -*- coding: utf-8 -*-
import logging

from lncrawl.core import Chapter, LegacyCrawler, Volume

logger = logging.getLogger(__name__)
search_url = "https://phoenixnovels.com.br/?s=%s&post_type=wp-manga"


class PhoenixNovels(LegacyCrawler):
    base_url = "https://phoenixnovels.com.br/"

    def initialize(self):
        self.cleaner.bad_css.update(
            [
                "div.padSection",
                "div#padSection",
            ]
        )

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            if not a:
                continue
            latest = tab.select_one(".latest-chap .chapter a")
            votes = tab.select_one(".rating .total_votes")
            results.append(
                {
                    "title": a.text.strip(),
                    "url": self.absolute_url(a["href"]),
                    "info": "%s | Rating: %s"
                    % (latest.text.strip() if latest else "N/A", votes.text.strip() if votes else "0"),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("#manga-title h1")
        if not possible_title:
            raise Exception("Título da novel não encontrado com o seletor '#manga-title h1'.")
        for span in possible_title.select("span"):
            span.extract()
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        # CORRIGIR CAPA
        image = soup.select_one(".summary_image img")
        if image:
            cover_url = image.get("data-src") or image.get("src")
            self.novel_cover = self.absolute_url(cover_url)
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = " ".join([a.text.strip() for a in soup.select('.author-content a[href*="novel-author"]')])
        logger.info("Author(s): %s", self.novel_author)

        chapter_list_url = self.absolute_url("ajax/chapters", self.novel_url)
        soup = self.post_soup(chapter_list_url, headers={"accept": "*/*"})

        chap_id = 0
        volume_id = 0

        for li in reversed(soup.select("li.parent.has-child")):
            volume_id += 1
            volume_title = li.select_one("a.has-child")
            if not volume_title:
                continue
            self.volumes.append(Volume(id=volume_id, title=volume_title.text.strip()))

            chapter_links = li.select(".wp-manga-chapter a[href]")
            for a in reversed(chapter_links):
                for span in a.find_all("span"):
                    span.extract()
                chap_id += 1
                self.chapters.append(
                    Chapter(
                        id=chap_id,
                        volume=volume_id,
                        title=a.text.strip(),
                        url=self.absolute_url(a["href"]),
                    )
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".reading-content") or soup.select_one(".text-left")
        return self.cleaner.extract_contents(contents)
