# -*- coding: utf-8 -*-

import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class Eight88NovelCrawler(Crawler):
    base_url = ["https://888novel.com/"]

    has_manga = False
    has_mtl = False

    def search_novel(self, query):
        query = query.replace(" ", "+")
        soup = self.get_soup(
            f"https://888novel.com/tim-kiem/?title={query}&he_liet=yes&status=all"
        )

        # The search result is paginated.
        urls = ["First"]

        list_page = soup.find("ul", {"class": "pagination"})
        if list_page:
            for a in list_page.find_all("a"):
                if a.get("href") != "#":
                    urls.append(a.get("href"))

        result = []
        for url in urls:
            # The first page is already loaded as soup
            if url != "First":
                soup = self.get_soup(url)

            for novel in soup.find("div", {"class": "col-lg-9"}).find_all(
                "li", {"class": "col-md-6 col-xs-12"}
            ):
                a = novel.find("h2", {"class": "crop-text-2"}).find("a")
                author = [
                    e.text
                    for e in novel.find("span", {"itemprop": "name"}).find_all("a")
                ]
                result.append(
                    {
                        "title": a.get("title"),
                        "url": a.get("href").strip(),
                        "info": self.cleaner.clean_text(
                            f"Author{'s' if len(author)>1 else ''} : {', '.join(author)}"
                        ),
                    }
                )
        return result

    def read_novel_info(self):
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1", {"class": "crop-text-1"}).text.strip()

        try:
            rows = soup.find("table").find_all("tr")
            self.novel_author = ", ".join(
                [
                    e.text.strip()
                    for e in rows[(1 if len(rows) == 3 else 0)].find_all("a")
                ]
            )
        except Exception:
            pass

        try:
            self.novel_cover = self.absolute_url(
                soup.find("div", {"class": "book3d"}).find("img").get("data-src")
            )
        except Exception:
            pass

        self.volumes = [{"id": 1}]
        self.chapters = []

        chapter_count = 1
        first_iteration = True
        next_page = None
        while next_page or first_iteration:
            if first_iteration:
                first_iteration = False
            else:
                soup = self.get_soup(next_page.get("href"))

            try:
                next_page = soup.find("ul", {"id": "id_pagination"}).find(
                    lambda tag: tag.name == "a" and tag.text == "»"
                )
            except AttributeError:
                next_page = None

            for chap in soup.find("ul", {"class": "listchap clearfix"}).find_all("a"):
                if not chap.get("href"):
                    continue

                self.chapters.append(
                    {
                        "title": self.cleaner.clean_text(chap.text),
                        "url": "https://888novel.com" + chap.get("href").strip(),
                        "volume": 1,
                        "id": chapter_count,
                    }
                )
                chapter_count += 1

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])
        content = soup.find("div", {"class": "reading"})
        return self.cleaner.extract_contents(content)
