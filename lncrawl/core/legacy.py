from abc import abstractmethod
from typing import Any, Dict, Iterable, List, Optional, Union

from ..utils.event_lock import EventLock
from .models import Chapter, Novel, SearchResult, Volume
from .template import CrawlerTemplate


class LegacyCrawler(CrawlerTemplate):
    def __init__(
        self,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
        origin: Optional[str] = None,
    ) -> None:
        if isinstance(self.base_url, str):
            self.base_url = [self.base_url]

        self.home_url = self.base_url[0]

        super().__init__(
            origin=self.home_url,
            workers=workers,
            parser=parser,
        )

        self._lock = EventLock()
        self.novel_url: str = ""
        self.novel_title: str = ""
        self.novel_author: str = ""
        self.novel_cover: Optional[str] = None
        self.is_rtl: bool = False
        self.novel_synopsis: str = ""
        self.novel_tags: List[str] = []
        self.volumes: List[Volume] = []
        self.chapters: List[Chapter] = []

    def close(self) -> None:
        self._lock.abort()
        super().close()

    # ------------------------------------------------------------------------- #
    # Task Manager
    # ------------------------------------------------------------------------- #

    @property
    def futures(self):
        return self.taskman.futures

    @property
    def workers(self):
        return self.taskman.workers

    @property
    def executor(self):
        return self.taskman.executor

    def init_executor(self, *args: Any, **kwargs: Any):
        return self.taskman.init_executor(*args, **kwargs)

    def submit_task(self, *args: Any, **kwargs: Any):
        return self.taskman.submit_task(*args, **kwargs)

    def progress_bar(self, *args: Any, **kwargs: Any):
        return self.taskman.progress_bar(*args, **kwargs)

    def cancel_futures(self, *args: Any, **kwargs: Any):
        return self.taskman.cancel_futures(*args, **kwargs)

    def resolve_as_generator(self, *args: Any, **kwargs: Any):
        return self.taskman.resolve_as_generator(*args, **kwargs)

    def resolve_futures(self, *args: Any, **kwargs: Any):
        return self.taskman.resolve_futures(*args, **kwargs)

    def as_completed(self, *args: Any, **kwargs: Any):
        return self.taskman.as_completed(*args, **kwargs)

    # ------------------------------------------------------------------------- #
    # Scraper
    # ------------------------------------------------------------------------- #

    @property
    def headers(self) -> Dict[str, Union[str, bytes]]:
        return dict(self.scraper.headers)

    @property
    def cookies(self) -> Dict[str, Optional[str]]:
        return {x.name: x.value for x in self.scraper.cookies}

    def get_response(self, *args: Any, **kwargs: Any):
        return self.scraper.get(*args, **kwargs)

    def post_response(self, *args: Any, **kwargs: Any):
        return self.scraper.post(*args, **kwargs)

    def submit_form(self, *args: Any, **kwargs: Any):
        return self.scraper.submit_form(*args, **kwargs)

    def download_file(self, url: str, output_file: str, **kwargs: Any):
        return self.scraper.get_file(url, output_file=output_file, **kwargs)

    def get_json(self, *args: Any, **kwargs: Any):
        return self.scraper.get_json(*args, **kwargs)

    def post_json(self, *args: Any, **kwargs: Any):
        return self.scraper.post_json(*args, **kwargs)

    def make_soup(self, *args: Any, **kwargs: Any):
        return self.scraper.make_soup(*args, **kwargs)

    def get_soup(self, *args: Any, **kwargs: Any):
        return self.scraper.get_soup(*args, **kwargs)

    def post_soup(self, *args: Any, **kwargs: Any):
        return self.scraper.post_soup(*args, **kwargs)

    # ------------------------------------------------------------------------- #
    # Crawler
    # ------------------------------------------------------------------------- #

    def search(self, query: str) -> Iterable[SearchResult]:
        return (
            SearchResult(**result) if isinstance(result, dict) else result
            for result in self.search_novel(query)
        )

    def read_novel(self, novel: Novel) -> None:
        with self._lock:
            self.novel_url = novel.url
            self.novel_title = novel.title or ""
            self.novel_author = novel.author or ""
            self.novel_cover = novel.cover_url or None
            self.is_rtl = novel.is_rtl or False
            self.novel_synopsis = novel.synopsis or ""
            self.novel_tags = []
            self.volumes = []
            self.chapters = []

            known_keys = set(dir(self))
            self.read_novel_info()
            new_keys = set(dir(self)) - known_keys
            novel.update({key: getattr(self, key) for key in new_keys})

            novel.is_rtl = self.is_rtl
            novel.is_mtl = self.has_mtl
            novel.language = self.language
            novel.is_manga = self.has_manga
            novel.title = self.novel_title
            novel.cover_url = self.novel_cover or ""
            novel.author = self.novel_author
            novel.synopsis = self.novel_synopsis
            novel.tags = self.novel_tags
            novel.volumes = self.volumes
            novel.chapters = self.chapters

    def download_chapter(self, chapter: Chapter) -> None:
        chapter.body = self.download_chapter_body(chapter)

    # ------------------------------------------------------------------------- #
    # Methods to implement in legacy crawler
    # ------------------------------------------------------------------------- #

    def search_novel(self, query: str) -> List[Union[SearchResult, Dict[str, Any]]]:
        raise NotImplementedError()

    @abstractmethod
    def read_novel_info(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def download_chapter_body(self, chapter: Chapter) -> str:
        raise NotImplementedError()
