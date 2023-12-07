# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class RulateCrawler(Crawler):
    base_url = [
        "https://tl.rulate.ru/",
    ]

    def initialize(self):
        self.cleaner.bad_css.update([".thumbnail"])

    def login(self, email: str, password: str):
        login_url = "https://tl.rulate.ru/"
        login_data = {
            'login[login]': email,
            'login[pass]': password
        }
        self.post_response(
            login_url,
            data=login_data
        )

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        chapters = soup.select_one("#Chapters")
        if not chapters:
            input_path = soup.find("input", {"name": "path", "type": "hidden"})
            if input_path:
                soup = self.submit_form_for_soup(
                    url="https://tl.rulate.ru/mature",
                    data={
                        "path": input_path["value"],
                        "ok": "Да",
                    },
                )
                chapters = soup.select_one("#Chapters")

        possible_title = soup.find("h1")
        if possible_title:
            self.novel_title = possible_title.text.split("/")[-1].strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_images = soup.find("div", {"class": "span2"})
        if possible_images:
            possible_image = possible_images.find("img")
            if possible_image:
                self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        possible_author = soup.find("strong", text="Автор:")
        if possible_author:
            possible_author = possible_author.parent.find("a")
            if possible_author:
                self.novel_author = possible_author.text
        logger.info("Novel author: %s", self.novel_author)

        possible_synopsis = soup.select_one("#Info > div:nth-child(3)")
        if possible_synopsis:
            self.novel_synopsis = self.cleaner.extract_contents(possible_synopsis)
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for tag in soup.find_all("a", {"class": "badge"}):
            self.novel_tags.append(tag.text)
        logger.info("Novel tags: %s", self.novel_tags)

        chap_id = 0
        vol_id = 1
        self.volumes.append({"id": vol_id})
        if chapters:
            for row in chapters.find_all("tr"):
                if not row.has_attr("class"):
                    continue

                if row["class"][0] == "volume_helper":
                    if chap_id:
                        vol_id = vol_id + 1
                    else:
                        self.volumes.pop()

                    self.volumes.append({"id": vol_id, "title": row.text})
                    continue

                if row.find("span", {"class": "disabled"}):
                    continue

                possible_chapter_ref = row.find("a", {"class": False, "href": True})
                if possible_chapter_ref:
                    chap_id = chap_id + 1
                    self.chapters.append(
                        {
                            "id": chap_id,
                            "volume": vol_id,
                            "url": self.absolute_url(possible_chapter_ref["href"]),
                            "title": possible_chapter_ref.text,
                        }
                    )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one(".content-text")
        self.cleaner.clean_contents(contents)
        return str(contents)
