import logging
from abc import abstractmethod
from typing import List, Union

from ..models import Chapter, SearchResult, Volume
from ..utils.cleaner import TextCleaner
from .scraper import Scraper

logger = logging.getLogger(__name__)


class Crawler(Scraper):
    """Blueprint for creating new crawlers"""

    has_manga = False
    has_mtl = False
    base_url: Union[str, List[str]]

    # ------------------------------------------------------------------------- #
    # Internal methods
    # ------------------------------------------------------------------------- #
    def __init__(self) -> None:
        super(Crawler, self).__init__()

        self.cleaner = TextCleaner()

        # Automatically available with all instances
        self.home_url = ""
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
    # Implement these methods
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
    def download_chapter_body(self, chapter) -> str:
        """Download body of a single chapter and return as clean html format."""
        raise NotImplementedError()

    def download_image(self, url) -> bytes:
        """Download image from url"""
        logger.info("Downloading image: " + url)
        response = self.get_response(
            url,
            headers={
                "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9"
            },
        )
        return response.content

    def get_chapter_index_of(self, url) -> int:
        """Return the index of chapter by given url or 0"""
        url = (url or "").strip().strip("/")
        for chapter in self.chapters:
            if chapter["url"] == url:
                return chapter["id"]

        return 0
