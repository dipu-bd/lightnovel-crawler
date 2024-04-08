# -*- coding: utf-8 -*-

import logging
from urllib.parse import urlparse, parse_qs
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class WebToonsCrawler(Crawler):
    has_manga = True
    base_url = ["https://www.webtoons.com/"]

    search_url = "%s/en/search?keyword=%s"

    def initialize(self) -> None:
        self.cleaner.bad_tags.update(["h3"])

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")

        search_url1 = self.search_url % (self.home_url, query)
        search_url2 = search_url1 + "&searchType=CHALLENGE"

        soup = self.get_soup(search_url1)
        soup1 = self.get_soup(search_url2)

        results = []
        for tab in soup.select("ul.card_lst li"):
            a = tab.select_one("a")
            title = tab.select_one("p.subj").get_text()
            results.append(
                {
                    "title": title,
                    "url": self.absolute_url(a["href"])
                }
            )

        for tab in soup1.select("div.challenge_lst.search ul"):
            a = tab.select_one("a.challenge_item")
            title = tab.select_one("p.subj").get_text()
            results.append(
                {
                    "title": title,
                    "url": self.absolute_url(a["href"])
                }
            )

        return results

    def read_novel_info(self):  # need to check if there is only 1 pagination
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1.subj")
        if possible_title is None:
            possible_title = soup.select_one("h3.subj")
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        self.novel_author = soup.select_one("a.author").text
        logger.info("%s", self.novel_author)

        last_link = soup.select_one("div.paginate a:nth-last-child(1)")

        url = str(last_link["href"])

        parsed_url = urlparse(url)
        query_params = parse_qs(parsed_url.query)
        page_number = query_params.get('page', [])[0] if 'page' in query_params else None
        page_number = int(page_number)

        futures = [
            self.executor.submit(self.get_soup, f"{self.novel_url}&page={i}")
            for i in range(1, page_number + 1)
        ]
        page_soups = [f.result() for f in futures]
        # url_selector : element["href"] , chap_title : element.select_one("span.subj").text

        num = 1
        numbers = []
        chap_links = []
        chap_titles = []

        for element in reversed(
            [a for soup in page_soups for a in soup.select("#_listUl a")]
        ):
            numbers.append(num)
            chap_links.append(element["href"])
            chap_titles.append(element.select_one("span.subj").text)
            num += 1

        data = {}
        sets_of_data = []

        for number, link, title in zip(numbers, chap_links, chap_titles):
            sets_of_data.append((number, link, title))

        for number, link, title in sets_of_data:
            data[number] = (link, title)

        for chap_num, (link, title) in data.items():
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if chap_id % 100 == 1:
                self.volumes.append({"id": vol_id})
            self.chapters.append(
                {
                    "id": chap_id,
                    "volume": vol_id,
                    "title": title,
                    "url": self.absolute_url(link),
                }
            )

    def download_chapter_body(self, chapter):
        logger.info("Visiting %s", chapter["url"])
        soup = self.get_soup(chapter["url"], headers={'Referer': f'{self.novel_url}'})
        contents = soup.select_one("#_imageList")

        for img in contents.findAll("img"):
            if img.has_attr("data-url"):
                src_url = img["data-url"]
                parent = img.parent
                img.extract()
                new_tag = soup.new_tag("img", src=src_url)
                parent.append(new_tag)

        return self.cleaner.extract_contents(contents)
