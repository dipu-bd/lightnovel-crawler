import logging
from lncrawl.core.crawler import Crawler
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class Lnmtlfr(Crawler):
    base_url = ["https://lnmtlfr.com/"]

    has_manga = False
    machine_translation = True

    def search_novel(self, query):
        query = query.replace(" ", "+")
        soup = self.get_soup(f"https://lnmtlfr.com/?s={query}&post_type=wp-manga")

        result = []
        for novel in soup.find_all("div", {"class": "row c-tabs-item__content"}):
            title = novel.find("div", {"class": "post-title"}).find("a")

            authors = (
                novel.find(
                    "div",
                    {"class": lambda x: x.startswith("post-content_item mg_author")},
                )
                .find("div", {"class": "summary-content"})
                .find_all("a")
            )

            result.append(
                {
                    "title": self.cleaner.clean_text(title.text),
                    "url": title.get("href"),
                    "info": f"Author{'s' if len(authors)>1 else ''} : "
                    + self.cleaner.clean_text(", ".join([a.text for a in authors])),
                }
            )

        return result

    def read_novel_info(self):

        soup = self.get_soup(self.novel_url)

        self.novel_title = self.cleaner.clean_text(
            soup.find("div", {"class": "post-title"}).find("h1").text
        )
        self.novel_cover = self.cleaner.clean_text(
            soup.find("div", {"class": "summary_image"}).find("img").get("src")
        )
        self.novel_author = self.cleaner.clean_text(
            ", ".join(
                [
                    e.text.strip()
                    for e in soup.find("div", {"class": "author-content"}).find_all("a")
                ]
            )
        )

        # Chapter are recuperated from a post request.
        # I didn't know how to make a post request using get_soup() so I just used requests.
        id = soup.find("input", {"class": "rating-post-id"}).get("value")

        url = "https://lnmtlfr.com/wp-admin/admin-ajax.php"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        data = f"action=manga_get_chapters&manga={id}"
        resp = requests.post(url, headers=headers, data=data)
        soup = BeautifulSoup(resp.text, "html.parser")

        list_vol = soup.find_all("ul", {"class": "sub-chap list-chap"})
        list_vol.reverse()

        chap_count = 1
        self.chapters = []

        if list_vol:
            self.volumes = []
            vol_count = 1
            for vol in list_vol:

                list_chap = vol.find_all("li")
                list_chap.reverse()
                for chap in list_chap:
                    self.chapters.append(
                        {
                            "id": chap_count,
                            "volume": vol_count,
                            "url": chap.find("a").get("href").strip(),
                            "title": self.cleaner.clean_text(chap.find("a").text),
                        }
                    )
                    chap_count += 1
                self.volumes.append({"id": vol_count})
                vol_count += 1
        else:
            self.volumes = [{"id": 1}]
            list_chap = soup.find_all("li")
            list_chap.reverse()
            for chap in list_chap:
                self.chapters.append(
                    {
                        "id": chap_count,
                        "volume": 1,
                        "url": chap.find("a").get("href").strip(),
                        "title": self.cleaner.clean_text(chap.find("a").text),
                    }
                )
                chap_count += 1

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        return self.cleaner.extract_contents(soup.find("div", {"class": "text-left"}))
