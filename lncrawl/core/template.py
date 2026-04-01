from abc import abstractmethod
from typing import Iterable, Union

from ..context import ctx
from ..exceptions import LNException
from .crawler import Crawler
from .models import Chapter, Novel, Volume
from .soup import PageSoup


class CrawlerTemplate(Crawler):
    """Class extended by all templates"""

    pass


class SoupTemplate(CrawlerTemplate):
    """General template for all soup-based crawlers"""

    novel_title_selector: str
    novel_cover_selector: str
    novel_author_selector: str
    novel_tags_selector: str
    novel_synopsis_selector: str
    chapter_list_selector: str
    chapter_title_selector: str
    chapter_url_selector: str
    chapter_body_selector: str

    def initialize(self) -> None:
        pass

    def login(self, username_or_email: str, password_or_token: str) -> None:
        pass

    def read_novel(self, novel: Novel) -> None:
        soup = self.get_soup(novel.url)

        try:
            novel.title = self.parse_title(soup)
        except Exception as e:
            raise LNException("Failed to parse novel title", e)

        try:
            novel.cover_url = self.parse_cover(soup)
        except Exception as e:
            ctx.logger.warn("Failed to parse novel cover | %s", e)

        try:
            novel.author = ", ".join(set(self.parse_authors(soup)))
        except Exception as e:
            ctx.logger.warn("Failed to parse novel authors | %s", e)

        try:
            novel.tags = list(set(self.parse_tags(soup)))
        except Exception as e:
            ctx.logger.warn("Failed to parse novel tags | %s", e)

        try:
            self.novel_synopsis = self.parse_summary(soup) or ""
        except Exception as e:
            ctx.logger.warn("Failed to parse novel synopsis | %s", e)

        novel.volumes = []
        novel.chapters = []
        for item in self.parse_chapter_list(soup):
            if isinstance(item, Chapter):
                novel.chapters.append(item)
            elif isinstance(item, Volume):
                novel.volumes.append(item)

    def download_chapter(self, chapter: Chapter) -> None:
        soup = self.get_soup(chapter.url)
        body = self.select_chapter_body(soup)
        if not body:
            raise LNException("No chapter contents")
        chapter.body = self.parse_chapter_body(body)

    def get_soup(self, url: str) -> PageSoup:
        return self.scraper.get_soup(url)

    def parse_title(self, soup: PageSoup) -> str:
        """Parse and return the novel title"""
        return soup.select_one(self.novel_title_selector).text

    def parse_cover(self, soup: PageSoup) -> str:
        """Parse and return the novel cover image"""
        return soup.select_one(self.novel_cover_selector).get("src")

    def parse_authors(self, soup: PageSoup) -> Iterable[str]:
        """Parse and return the novel authors"""
        for author in soup.select(self.novel_author_selector):
            if author.text:
                yield author.text

    def parse_tags(self, soup: PageSoup) -> Iterable[str]:
        """Parse and return the novel categories/genres/tags"""
        for tag in soup.select(self.novel_tags_selector):
            if tag.text:
                yield tag.text

    def parse_summary(self, soup: PageSoup) -> str:
        """Parse and return the novel summary or synopsis"""
        return soup.select_one(self.novel_synopsis_selector).text

    @abstractmethod
    def parse_chapter_list(self, soup: PageSoup) -> Iterable[Union[Chapter, Volume]]:
        """Parse and set the volumes and chapters"""
        chapter_id = 1
        for chapter in soup.select(self.chapter_list_selector):
            yield Chapter(
                id=chapter_id,
                title=chapter.text,
                url=chapter.get("href"),
            )
            chapter_id += 1

    @abstractmethod
    def select_chapter_body(self, soup: PageSoup) -> PageSoup:
        """Select the tag containing the chapter text"""
        return soup.select_one(self.chapter_body_selector)

    def parse_chapter_body(self, soup: PageSoup) -> str:
        """Extract the clean HTML content from the tag containing the chapter text"""
        return self.cleaner.extract_contents(soup)
