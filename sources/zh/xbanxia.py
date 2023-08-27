import logging
import re
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)

search_url = 'https://www.xbanxia.com/modules/article/search_t.php'
headers = {'Content-Type': 'application/x-www-form-urlencoded',
           'Cookie': 'jieqiUserCharset=utf-8;',
           'Origin': 'https://www.xbanxia.com',
           'Referer': 'https://www.xbanxia.com/',
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1788.0'}


class Xbanxia(Crawler):
    base_url = ['https://www.xbanxia.com/']
    has_manga = False
    has_mtl = False

    def search_novel(self, query):

        logger.debug(f"Searching {query} on Xbanxia")

        data = {'searchkey': f'{query}', 'submit': ''}
        soup = self.post_soup(search_url, data , headers,)

        results = []
        for tab in soup.select("div ol li"):
            a = tab.select_one("a")
            author = tab.select_one("ol li span").text
            results.append(
                {
                    "title": a["title"],
                    "url": self.absolute_url(a["href"]),
                    "author": "%s" % (author),
                }
            )

        return results

    def read_novel_info(self):
        logger.debug("Visiting %s", self.novel_url)
        soup = self.get_soup(self.novel_url)

        possible_title = soup.select_one("div.book-describe h1")
        assert possible_title, "No novel title"
        self.novel_title = possible_title.text
        logger.info("Novel title: %s", self.novel_title)

        author = soup.find_all(href=re.compile("author"))
        if len(author) == 2:
            self.novel_author = author[0].text + " (" + author[1].text + ")"
        else:
            self.novel_author = author[0].text
        logger.info("Novel author: %s", self.novel_author)

        self.novel_cover = self.absolute_url(
            soup.select_one("div.book-img img")["data-original"]
        )
        logger.info("Novel cover: %s", self.novel_cover)

        for div in soup.select("div.book-list ul li"):
            vol_title = div.select_one("a").text
            vol_id = [int(x) for x in re.findall(r"\d+", vol_title)]
            vol_id = vol_id[0] if len(vol_id) else len(self.volumes) + 1
            self.volumes.append(
                {
                    "id": vol_id,
                    "title": vol_title,
                }
            )

            for a in div.select("a"):
                ch_title = a.text
                ch_id = [int(x) for x in re.findall(r"\d+", ch_title)]
                ch_id = ch_id[0] if len(ch_id) else len(self.chapters) + 1
                self.chapters.append(
                    {
                        "id": ch_id,
                        "volume": vol_id,
                        "title": ch_title,
                        "url": self.absolute_url(a["href"]),
                    }
                )

        logger.debug(
            "%d chapters and %d volumes found", len(self.chapters), len(self.volumes)
        )

    def download_chapter_body(self, chapter):
        soup = self.get_soup(chapter["url"])

        contents = soup.select_one("div#nr1")
        return str(contents)
