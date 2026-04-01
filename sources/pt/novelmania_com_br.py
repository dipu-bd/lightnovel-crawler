import logging
from typing import Generator

from lncrawl.core import Chapter, PageSoup, Volume
from lncrawl.templates.soup.with_volume import ChapterWithVolumeSoupTemplate

logger = logging.getLogger(__name__)


class NovelmaniaComBrCrawler(ChapterWithVolumeSoupTemplate):
    base_url = ["https://novelmania.com.br/"]
    has_manga = False
    has_mtl = False

    def initialize(self) -> None:
        super().initialize()

    def parse_title(self, soup: PageSoup) -> str:
        tag = soup.select_one(".novel-info h1")
        assert tag, "No title tag"
        return tag.get_text(strip=True)

    def parse_cover(self, soup: PageSoup) -> str:
        tag = soup.select_one(".novel-img img[src]")
        if not tag:
            return ""
        return self.absolute_url(tag["src"])

    def parse_authors(self, soup: PageSoup) -> Generator[str, None, None]:
        for b in soup.select(".novel-info span b"):
            if "Autor" in b.get_text():
                tag = b.parent
                if tag:
                    b.extract()
                    yield tag.get_text(strip=True)

    def parse_genres(self, soup: PageSoup) -> Generator[str, None, None]:
        for a in soup.select('#info .tags a[href^="/genero/"]'):
            tag = a["title"]
            if isinstance(tag, str):
                yield tag

    def parse_summary(self, soup: PageSoup) -> str:
        desc = soup.select_one("#info .text")
        if not desc:
            return ""
        return self.cleaner.extract_contents(desc)

    def select_volume_tags(self, soup: PageSoup) -> Generator[PageSoup, None, None]:
        yield from soup.select("#accordion .card-header button")

    def select_chapter_tags(self, tag: PageSoup, vol: Volume, soup: PageSoup) -> Generator[PageSoup, None, None]:
        yield from soup.select(f"{tag['data-target']} li a[href]")

    def parse_chapter_item(self, tag: PageSoup, id: int, vol: Volume) -> Chapter:
        title_tag = tag.select_one("strong")
        if title_tag:
            title = title_tag.get_text(strip=True)
        else:
            title = f"Chapter {id}"
        return Chapter(
            id=id,
            title=title,
            volume=vol.id,
            url=self.absolute_url(tag["href"]),
        )

    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        body = soup.select_one("#chapter-content")
        assert body, "No chapter body"
        return body
