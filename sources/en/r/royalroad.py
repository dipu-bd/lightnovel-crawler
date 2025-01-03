# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)
search_url = "https://www.royalroad.com/fictions/search?keyword=%s"


class RoyalRoadCrawler(Crawler):
    base_url = "https://www.royalroad.com/",
    watermark_set = {
        "This book's true home is on another platform. Check it out there for the real experience.",
        "This tale has been unlawfully lifted from Royal Road. If you spot it on Amazon, please report it.",
        "This novel's true home is a different platform. Support the author by finding it there.",
        "Stolen from its rightful place, this narrative is not meant to be on Amazon; report any sightings.",
        "If you discover this tale on Amazon, be aware that it has been stolen. Please report the violation.",
        "If you find this story on Amazon, be aware that it has been stolen. Please report the infringement.",
        "Enjoying this book? Seek out the original to ensure the author gets credit.",
        "Did you know this text is from a different site? Read the official version to support the creator.",
        "The tale has been illicitly lifted; should you spot it on Amazon, report the violation.",
        "The tale has been taken without authorization; if you see it on Amazon, report the incident.",
        "Ensure your favorite authors get the support they deserve. Read this novel on Royal Road.",
        "Reading on Amazon or a pirate site? This novel is from Royal Road. Support the author by reading it there.",
        "The tale has been stolen; if detected on Amazon, report the violation.",
        "A case of content theft: this narrative is not rightfully on Amazon; if you spot it, report the violation.",
        "Love this novel? Read it on Royal Road to ensure the author gets credit.",
        "The story has been stolen; if detected on Amazon, report the violation.",
        "If you come across this story on Amazon, be aware that it has been stolen from Royal Road. Please report it.",
        "Stolen from its original source, this story is not meant to be on Amazon; report any sightings.",
        "The author's narrative has been misappropriated; report any instances of this story on Amazon.",
        "If you come across this story on Amazon, it's taken without permission from the author. Report it.",
        "The author's tale has been misappropriated; report any instances of this story on Amazon.",
        "Stolen from its rightful author, this tale is not meant to be on Amazon; report any sightings.",
        "Stolen content alert: this content belongs on Royal Road. Report any occurrences.",
        "Did you know this story is from Royal Road? Read the official version for free and support the author.",
        "Unauthorized duplication: this tale has been taken without consent. Report sightings.",
        "This narrative has been unlawfully taken from Royal Road. If you see it on Amazon, please report it.",
        "Stolen content warning: this content belongs on Royal Road. Report any occurrences.",
        "Help support creative writers by finding and reading their stories on the original site.",
        "If you stumble upon this narrative on Amazon, it's taken without the author's consent. Report it.",
        "If you discover this narrative on Amazon, be aware that it has been stolen. Please report the violation.",
        "If you spot this narrative on Amazon, know that it has been stolen. Report the violation.",
        "This tale has been unlawfully lifted without the author's consent. Report any appearances on Amazon.",
        "If you encounter this tale on Amazon, note that it's taken without the author's consent. Report it.",
        "This tale has been pilfered from Royal Road. If found on Amazon, kindly file a report.",
        "This story has been stolen from Royal Road. If you read it on Amazon, please report it",
        "Enjoying the story? Show your support by reading it on the official site.",
        "The genuine version of this novel can be found on another site. Support the author by reading it there.",
        "This story is posted elsewhere by the author. Help them out by reading the authentic version.",
        "Love what you're reading? Discover and support the author on the platform they originally published on.",
        "Stolen story; please report.",
        "The narrative has been stolen; if detected on Amazon, report the infringement.",
        "Support the creativity of authors by visiting the original site for this novel and more.",
        "This tale has been unlawfully obtained from Royal Road. If you discover it on Amazon, kindly report it.",
        "Reading on this site? This novel is published elsewhere. Support the author by seeking out the original.",
        "Stolen from Royal Road, this story should be reported if encountered on Amazon.",
        "This story originates from a different website. Ensure the author gets the support they deserve by reading it there.",
    }

    def initialize(self):
        self.init_executor(1)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select("h2.fiction-title a")[:5]:
            url = self.absolute_url(a["href"])
            results.append(
                {
                    "url": url,
                    "title": a.text.strip(),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "font-white"}).text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_cover = self.absolute_url(
            soup.find("img", {"class": "thumbnail inline-block"})["src"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = soup.find("a", {"class": "font-white"}).text.strip()
        logger.info("Novel author: %s", self.novel_author)

        self.novel_synopsis = self.cleaner.extract_contents(
            soup.find("div", {"class": "hidden-content"})
        )
        logger.info("Novel synopsis: %s", self.novel_synopsis)

        for tag in soup.find_all("a", {"class": "fiction-tag"}):
            self.novel_tags.append(tag.text)
        logger.info("Novel tags: %s", self.novel_tags)

        chapter_rows = soup.find("tbody").findAll("tr")
        chapters = [row.find("a", href=True) for row in chapter_rows]

        for x in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(x["href"]),
                    "title": x.text.strip() or ("Chapter %d" % chap_id),
                }
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        possible_title = soup.select_one("h2")
        if possible_title and "Chapter" in possible_title.text:
            chapter["title"] = possible_title.text.strip()

        chapter_contents = soup.select(".chapter-content")
        for chapter_content in chapter_contents:
            for html_tags in chapter_content.contents:
                if html_tags.name == 'div' and html_tags.string in self.watermark_set:
                    html_tags.decompose()

        contents = soup.select_one(".chapter-content")
        self.cleaner.clean_contents(contents)
        return str(contents)
