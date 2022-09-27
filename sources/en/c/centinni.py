# -*- coding: utf-8 -*-
import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = (
    "https://www.centinni.com/?s=%s&post_type=wp-manga&author=&artist=&release="
)


class Centinni(Crawler):
    base_url = "https://www.centinni.com/"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(
            [
                "a" "h3",
            ]
        )
        self.cleaner.bad_text_regex.update(
            [
                r"^Link for previous chapters:",
                r"^https://www.novelupdates.com/series/possessing-nothing/",
                r"^This translation belongs to Centinni.",
                r"^https://discord.gg/aqDszgB",
                r"^Hey guys, join us now on our discord server:",
                r"^https://www.paypal.me/centinni1",
                r"^You may also donate through paypal to support the people who work on "
                + "these novels (please specify which novel you are supporting):",
                r"^. And get a chance to chat with your favorite translators and editors."
                + " Meet more like-minded people and have a fun time with real-time novel "
                + "updates and much more.",
                r"^You may also donate through paypal to support the people who work on these"
                + " novels (please specify which novel you are supporting):",
                r"^You can donate on Ko-fi(from main page) Extra chapter be released when"
                + " 10$/chapter have been slowly accumulated on Ko-fi. Please mention the "
                + "novel you are supporting.",
                r"^Centinni is translating this novel.",
                r"^Possessing Nothing now has a chat channel! Join our discord server to "
                + "chat with your team and more friends!",
            ]
        )

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for tab in soup.select(".c-tabs-item__content"):
            a = tab.select_one(".post-title h3 a")
            latest = tab.select_one(".latest-chap .chapter a").text
            votes = tab.select_one(".rating .total_votes").text
            results.append(
                {
                    "title": a.text.strip(),
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

        volumes = set()
        chapters = soup.select("ul.main li.wp-manga-chapter a")
        for a in reversed(chapters):
            chap_id = len(self.chapters) + 1
            vol_id = (chap_id - 1) // 100 + 1
            volumes.add(vol_id)
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "url": self.absolute_url(a["href"]),
                    "title": a.text.strip() or ("Chapter %d" % chap_id),
                }
            )

        self.volumes = [{"id": x} for x in volumes]

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div.text-left")
        return self.cleaner.extract_contents(contents)
