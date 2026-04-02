# -*- coding: utf-8 -*-

import logging

from lncrawl.core import Chapter, LegacyCrawler, PageSoup, Volume

logger = logging.getLogger(__name__)
search_url = "https://mtled-novels.com/search_novel.php?q=%s"
login_url = "https://mtled-novels.com/login/ajax/checklogin.php"
logout_url = "https://mtled-novels.com/login/logout.php"


class MtledNovelsCrawler(LegacyCrawler):
    base_url = "https://mtled-novels.com/"

    def login(self, username, password):
        """login to LNMTL"""
        # Get the login page
        logger.info("Visiting %s", self.scraper.origin)
        self.get_response(self.scraper.origin)

        # Send post request to login
        logger.info("Logging in...")
        response = self.submit_form(
            login_url,
            data=dict(
                myusername=username,
                mypassword=password,
                remember=0,
            ),
        )

        # Check if logged in successfully
        data = response.json()
        logger.debug(data)
        if "response" in data and data["response"] == "true":
            print("Logged In")
        else:
            soup = PageSoup.create(data["response"], parser="lxml")
            soup.find("button").extract()
            error = soup.find("div").text.strip()
            raise PermissionError(error)

    def search_novel(self, query):
        query = query.lower().replace(" ", "+")
        soup = self.get_soup(search_url % query)

        results = []
        for a in soup.select(".card .row .col-lg-2 a")[:5]:
            url = self.absolute_url(a["href"])
            results.append(
                {
                    "url": url,
                    "title": a.img["alt"],
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text.strip()
        logger.info("Novel title: %s", self.novel_title)

        possible_image = soup.select_one("div.profile__img img")
        if possible_image:
            self.novel_cover = self.absolute_url(possible_image["src"])
        logger.info("Novel cover: %s", self.novel_cover)

        self.novel_author = "Downloaded from mtled-novels.com"
        logger.info("Novel author: %s", self.novel_author)

        chapters = soup.select("div#tab-profile-2 a")

        for a in chapters:
            chap_id = len(self.chapters) + 1
            vol_id = 1 + len(self.chapters) // 100
            if len(self.volumes) < vol_id:
                self.volumes.append(Volume(id=vol_id))
            self.chapters.append(
                Chapter(
                    id=chap_id,
                    volume=vol_id,
                    url=self.absolute_url(a["href"]),
                    title=a.text.strip() or "Chapter %d" % chap_id,
                )
            )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select("div.translated p")
        for p in soup.select("div.translated p"):
            for span in p.find_all("span"):
                if span:
                    span.unwrap()

        body = [str(p) for p in contents if p.text.strip()]
        return "<p>" + "</p><p>".join(body) + "</p>"
