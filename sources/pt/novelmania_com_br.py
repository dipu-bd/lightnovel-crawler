import logging
from typing import Iterable, Optional

from lncrawl.core import BrowserTemplate, Novel, PageSoup, Volume

logger = logging.getLogger(__name__)


class NovelmaniaComBrCrawler(BrowserTemplate):
    base_url = ["https://novelmania.com.br/"]
    has_manga = False
    has_mtl = False

    novel_title_selector = ".novel-info h1"
    novel_cover_selector = ".novel-img img[src]"
    novel_summary_selector = "#info .text"

    volume_list_selector = "#accordion .card-header button"
    chapter_title_selector = "strong"
    chapter_body_selector = "#chapter-content"

    def parse_author(self, soup: PageSoup, novel: Novel) -> None:
        authors = []
        for b in soup.select(".novel-info span b"):
            if "Autor" in b.text:
                tag = b.parent
                b.extract()
                authors.append(tag.text)
        novel.author = ", ".join(authors)

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        for a in soup.select('#info .tags a[href^="/genero/"]'):
            novel.tags.append(a["title"])

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        return tag.body.select(f"{tag['data-target']} li a[href]")
