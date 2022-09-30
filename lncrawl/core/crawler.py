import logging
from abc import abstractmethod
from typing import List

from ..models import Chapter, SearchResult, Volume
from ..utils.cleaner import TextCleaner
from .scraper import Scraper

logger = logging.getLogger(__name__)


class Crawler(Scraper):
    """Blueprint for creating new crawlers"""

    has_manga = False
    has_mtl = False
    base_url: List[str]

    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(self) -> None:
        super(Crawler, self).__init__(self.base_url[0])

        self.cleaner = TextCleaner()

        # Available in `search_novel` or `read_novel_info`
        self.novel_url = ""

        # Must resolve these fields inside `read_novel_info`
        self.novel_title = ""
        self.novel_author = ""
        self.novel_cover = None
        self.is_rtl = False

        # Each item must contain these keys:
        # `id` - 1 based index of the volume
        # `title` - the volume title (can be ignored)
        self.volumes: List[Volume] = []

        # Each item must contain these keys:
        # `id` - 1 based index of the chapter
        # `title` - the title name
        # `volume` - the volume id of this chapter
        # `volume_title` - the volume title (can be ignored)
        # `url` - the link where to download the chapter
        self.chapters: List[Chapter] = []

    def destroy(self) -> None:
        super(Crawler, self).destroy()
        self.volumes.clear()
        self.chapters.clear()

    # ------------------------------------------------------------------------- #
    # Methods to implement in crawler
    # ------------------------------------------------------------------------- #

    def initialize(self) -> None:
        pass

    def login(self, email: str, password: str) -> None:
        pass

    def logout(self) -> None:
        pass

    def search_novel(self, query: str) -> List[SearchResult]:
        """Gets a list of results matching the given query"""
        return []

    @abstractmethod
    def read_novel_info(self) -> None:
        """Get novel title, autor, cover etc"""
        raise NotImplementedError()

    @abstractmethod
    def download_chapter_body(self, chapter: Chapter) -> str:
        """Download body of a single chapter and return as clean html format."""
        raise NotImplementedError()

    def get_chapter_index_of(self, url: str) -> int:
        """Return the index of chapter by given url or 0"""
        url = (url or "").strip().strip("/")
        for chapter in self.chapters:
            if chapter["url"] == url:
                return chapter["id"]

        return 0
