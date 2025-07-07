import logging
from lncrawl.core.crawler import Crawler

logger = logging.getLogger(__name__)


class NovelFireCrawler(Crawler):
    base_url = [
        "https://novelfire.net/",
    ]
    has_mtl = False
    has_mange = False

    def initialize(self) -> None:
        self.init_executor(ratelimit=3)

    def read_novel_info(self) -> None:
        soup = self.get_soup(self.novel_url)

        self.novel_title = soup.find("h1").text.strip()
        self.novel_author = soup.select_one('span[itemprop="author"]').text.strip()

        img = soup.select_one(".cover img")
        self.novel_cover = self.absolute_url(img["data-src"])

        vol_id = 1
        vol_url = self.novel_url + "/chapters"

        while vol_url:
            soup = self.get_soup(self.absolute_url(vol_url))

            chapters = soup.select("ul.chapter-list li a")
            for a in chapters:
                chap_id = len(self.chapters) + 1
                self.chapters.append({
                    "id": chap_id,
                    "volume": vol_id,
                    "title": a["title"],
                    "url": self.absolute_url(a["href"]),
                })

            self.volumes.append({"id": vol_id})

            next_vol_a = soup.select_one("a.page-link[rel='next']")
            if next_vol_a:
                vol_url = next_vol_a['href']
                vol_id += 1
            else:
                vol_url = False
                break

    def download_chapter_body(self, chapter) -> str:
        soup = self.get_soup(chapter["url"])
        contents = soup.select_one("div#content")
        return self.cleaner.extract_contents(contents)
