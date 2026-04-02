from typing import Iterable, Optional, overload

from ..context import ctx
from ..exceptions import LNException
from .crawler import Crawler
from .models import Chapter, Novel, SearchResult, Volume
from .soup import PageSoup


class CrawlerTemplate(Crawler):
    """Class extended by all templates"""

    pass


class SoupTemplate(CrawlerTemplate):
    """General template for all soup-based crawlers"""

    search_item_list_selector = ""
    search_item_title_selector = ""
    search_item_url_selector = ""
    search_item_info_selector = ""

    novel_title_selector = 'meta[property="og:title"], meta[name="title"], title'
    novel_cover_selector = 'meta[property="og:image"], meta[name="image"]'
    novel_author_selector = 'meta[property="og:author"], meta[name="author"]'
    novel_tags_selector = 'meta[property="og:tag"], meta[name="keywords"]'
    novel_synopsis_selector = 'meta[property="og:description"], meta[name="description"]'

    volume_list_reverse = False
    volume_list_selector = ""
    volume_title_selector = ""

    chapter_list_reverse = False
    chapter_list_selector = ""
    chapter_title_selector = ""
    chapter_url_selector = ""

    chapter_body_selector = ""

    # ------------------------------------------------------------------------- #
    # Crawler method implementations
    # ------------------------------------------------------------------------- #

    def search(self, query: str) -> Iterable[SearchResult]:
        return (self.parse_search_item(tag) for tag in self.select_search_item_list(query))

    def read_novel(self, novel: Novel) -> None:
        soup = self.get_novel_soup(novel)

        try:
            self.parse_title(soup, novel)
        except Exception as e:
            raise LNException("Failed to parse novel title") from e

        try:
            self.parse_cover(soup, novel)
        except Exception:
            ctx.logger.warn("Failed to parse novel cover", exc_info=True)

        try:
            self.parse_authors(soup, novel)
        except Exception:
            ctx.logger.warn("Failed to parse novel authors", exc_info=True)

        try:
            self.parse_tags(soup, novel)
        except Exception:
            ctx.logger.warn("Failed to parse novel tags", exc_info=True)

        try:
            self.parse_summary(soup, novel)
        except Exception:
            ctx.logger.warn("Failed to parse novel synopsis", exc_info=True)

        try:
            novel.volumes = []
            novel.chapters = []
            self.parse_toc(soup, novel)
        except Exception as e:
            raise LNException("Failed to parse chapter list") from e

    def download_chapter(self, chapter: Chapter) -> None:
        url = self.build_chapter_url(chapter)
        soup = self.scraper.get_soup(url)
        body = soup.select_one(self.chapter_body_selector)
        self.parse_chapter_body(body, chapter)

    # ------------------------------------------------------------------------- #
    # Parser methods for Search Results
    # ------------------------------------------------------------------------- #

    def build_search_url(self, query: str) -> str:
        """Get the search url for the given query"""
        # Example: return f"{self.scraper.origin}?{urlencode({"query": query)}"
        raise NotImplementedError()

    def select_search_item_list(self, query: str) -> Iterable[PageSoup]:
        """Select search items from the search page"""
        url = self.build_search_url(query)
        soup = self.scraper.get_soup(url)
        return soup.select(self.search_item_list_selector)

    def parse_search_item(self, soup: PageSoup) -> SearchResult:
        """Parse a tag and return single search result"""
        return SearchResult(
            title=self.parse_search_item_title(soup),
            url=self.parse_search_item_url(soup),
            info=self.parse_search_item_info(soup),
        )

    def parse_search_item_title(self, soup: PageSoup) -> str:
        """Parse and return the search item title"""
        title_tag = soup.select_one(self.search_item_title_selector) or soup
        return title_tag.text

    def parse_search_item_url(self, soup: PageSoup) -> str:
        """Parse and return the search item url"""
        url_tag = soup.select_one(self.search_item_url_selector) or soup
        return self.absolute_url(url_tag.get("href"))

    def parse_search_item_info(self, soup: PageSoup) -> str:
        """Parse and return the search item info"""
        info_tag = soup.select_one(self.search_item_info_selector) or soup
        return info_tag.text

    # ------------------------------------------------------------------------- #
    # Parser methods for Novel information
    # ------------------------------------------------------------------------- #

    def get_novel_soup(self, novel: Novel) -> PageSoup:
        url = self.build_novel_url(novel)
        return self.scraper.get_soup(url)

    def build_novel_url(self, novel: Novel) -> str:
        """Build the novel url"""
        return self.absolute_url(novel.url)

    def parse_title(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel title"""
        tag = soup.select_one(self.novel_title_selector)
        novel.title = tag.text
        if not novel.title:
            novel.title = soup.select_one(SoupTemplate.novel_title_selector).text

    def parse_cover(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel cover image"""
        cover_tag = soup.select_one(self.novel_cover_selector)
        for attr in ["data-lazy-src", "data-src", "src", "content"]:
            src_url = cover_tag.get(attr)
            if src_url:
                novel.cover_url = self.absolute_url(src_url)
                break
        if not novel.title:
            novel.cover_url = soup.select_one(SoupTemplate.novel_cover_selector).get("content")

    def parse_authors(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel authors"""
        novel.author = ", ".join(
            [author.text for author in soup.select(self.novel_author_selector)]
        )
        if not novel.author:
            novel.author = soup.select_one(SoupTemplate.novel_author_selector).text

    def parse_tags(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel categories/genres/tags"""
        novel.tags = [tag.text for tag in soup.select(self.novel_tags_selector)]
        if not novel.tags:
            default_tags = soup.select_one(SoupTemplate.novel_tags_selector)
            novel.tags = [t.strip() for t in default_tags.text.split(",")]

    def parse_summary(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the novel summary or synopsis"""
        tag = soup.select_one(self.novel_synopsis_selector)
        novel.summary = self.cleaner.extract_contents(tag)
        if not novel.summary:
            default_summary = soup.select_one(SoupTemplate.novel_synopsis_selector)
            novel.summary = self.cleaner.extract_contents(default_summary)

    # ------------------------------------------------------------------------- #
    # Parser methods for Volume list
    # ------------------------------------------------------------------------- #

    def parse_toc(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the table of contents (volumes and chapters)"""
        self.parse_volume_list(soup, novel)
        if not novel.volumes:
            self.parse_chapter_list(soup, novel)

    def parse_volume_list(self, soup: PageSoup, novel: Novel) -> None:
        """Parse and set the volumes and chapters"""
        volume_tags = self.select_volume_tags(soup, novel)
        for tag in volume_tags:
            volume_id = len(novel.volumes) + 1
            volume = self.parse_volume_item(tag, volume_id)
            self.parse_chapter_list(tag, novel, volume)
            novel.volumes.append(volume)

    def parse_volume_item(self, soup: PageSoup, volume_id: int) -> Volume:
        """Parse a single volume from volume list item tag"""
        volume = Volume(id=volume_id)
        self.parse_volume_title(soup, volume)
        return volume

    def select_volume_tags(self, soup: PageSoup, novel: Novel) -> Iterable[PageSoup]:
        """Select volume tags from the novel page"""
        volume_tags = soup.select(self.volume_list_selector)
        if self.volume_list_reverse:
            return reversed(volume_tags)
        return volume_tags

    def parse_volume_title(self, soup: PageSoup, volume: Volume) -> None:
        """Parse a single volume from volume list item tag"""
        title_tag = soup.select_one(self.volume_title_selector) or soup
        volume.title = title_tag.text

    # ------------------------------------------------------------------------- #
    # Parser methods for Chapter list
    # ------------------------------------------------------------------------- #

    @overload
    def parse_chapter_list(self, tag: PageSoup, novel: Novel) -> None: ...

    @overload
    def parse_chapter_list(self, tag: PageSoup, novel: Novel, volume: Volume) -> None: ...

    def parse_chapter_list(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> None:
        """Parse and set the chapters for the novel (optionally scoped to a volume)."""
        if volume is None:
            chapter_tags = self.select_chapter_tags(tag, novel)
        else:
            chapter_tags = self.select_chapter_tags(tag, novel, volume)

        for chapter_tag in chapter_tags:
            chapter_id = len(novel.chapters) + 1
            chapter = self.parse_chapter_item(chapter_tag, chapter_id)
            if volume is not None:
                chapter.volume = volume.id
            novel.chapters.append(chapter)

    @overload
    def select_chapter_tags(self, tag: PageSoup, novel: Novel) -> Iterable[PageSoup]: ...

    @overload
    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Volume
    ) -> Iterable[PageSoup]: ...

    def select_chapter_tags(
        self, tag: PageSoup, novel: Novel, volume: Optional[Volume] = None
    ) -> Iterable[PageSoup]:
        """Select chapter tags from the novel page (optionally scoped to a volume)."""
        chapter_tags = tag.select(self.chapter_list_selector)
        if self.chapter_list_reverse:
            return reversed(chapter_tags)
        return chapter_tags

    def parse_chapter_item(self, soup: PageSoup, chapter_id: int) -> Chapter:
        """Parse a single chapter from chapter list item tag"""
        chapter = Chapter(id=chapter_id)
        self.parse_chapter_title(soup, chapter)
        self.parse_chapter_url(soup, chapter)
        return chapter

    def parse_chapter_title(self, soup: PageSoup, chapter: Chapter) -> None:
        """Parse and set the chapter title"""
        title_tag = soup.select_one(self.chapter_title_selector) or soup
        chapter.title = title_tag.text

    def parse_chapter_url(self, soup: PageSoup, chapter: Chapter) -> None:
        """Parse and set the chapter url"""
        url_tag = soup.select_one(self.chapter_url_selector) or soup
        chapter.url = self.absolute_url(url_tag.get("href"))

    # ------------------------------------------------------------------------- #
    # Parser methods for Chapter body
    # ------------------------------------------------------------------------- #

    def build_chapter_url(self, chapter: Chapter) -> str:
        """Build the chapter url"""
        return self.absolute_url(chapter.url)

    def parse_chapter_body(self, soup: PageSoup, chapter: Chapter) -> None:
        """Extract the clean HTML content from the tag containing the chapter text"""
        chapter.body = self.cleaner.extract_contents(soup)
