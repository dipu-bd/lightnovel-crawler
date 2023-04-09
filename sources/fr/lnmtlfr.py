import logging

from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Lnmtlfr(Crawler):
    base_url = ["https://lnmtlfr.com/"]

    has_manga = False
    has_mtl = True

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

            author_names = ", ".join([a.text for a in authors])

            result.append(
                {
                    "title": title.text,
                    "url": title.get("href"),
                    "info": f"Author{'s' if len(authors) > 1 else ''}: {author_names}",
                }
            )

        return result

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = (
            soup.find("div", {"class": "post-title"}).find("h1").text.strip()
        )
        self.novel_cover = self.absolute_url(
            soup.find("div", {"class": "summary_image"}).find("img").get("src")
        )

        self.novel_synopsis = self.cleaner.extract_contents(soup.find("div", {"class": "summary__content"}).find("p"))
        self.language = "fr"

        self.novel_author = ", ".join(
            [
                e.text.strip()
                for e in soup.find("div", {"class": "author-content"}).find_all("a")
            ]
        )

        # Chapter are recuperated from a post request.
        id = soup.find("input", {"class": "rating-post-id"}).get("value")

        url = "https://lnmtlfr.com/wp-admin/admin-ajax.php"
        data = f"action=manga_get_chapters&manga={id}"
        resp = self.submit_form(url, data=data)
        soup = self.make_soup(resp)

        list_vol = soup.find_all("ul", {"class": "sub-chap list-chap"})
        if list_vol:
            self.volumes = []
            for vol in reversed(list_vol):
                vol_id = len(self.volumes) + 1
                self.volumes.append({"id": vol_id})

                list_chap = vol.find_all("li")
                for chap in reversed(list_chap):
                    chap_id = len(self.chapters) + 1
                    self.chapters.append(
                        {
                            "id": chap_id,
                            "volume": vol_id,
                            "title": chap.find("a").text,
                            "url": self.absolute_url(chap.find("a").get("href")),
                        }
                    )
        else:
            self.volumes = [{"id": 1}]
            list_chap = soup.find_all("li")
            for chap in reversed(list_chap):
                chap_id = len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": chap_id,
                        "volume": 1,
                        "title": chap.find("a").text,
                        "url": self.absolute_url(chap.find("a").get("href")),
                    }
                )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.find("div", {"class": "text-left"})
        return self.cleaner.extract_contents(content)
