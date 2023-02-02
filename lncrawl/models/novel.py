from enum import Enum
from typing import List, Optional

from box import Box

from .chapter import Chapter
from .volume import Volume
from ..assets.languages import language_codes


class NovelStatus(str, Enum):
    unknown = "Unknown"
    ongoing = "Ongoing"
    completed = "Completed"
    hiatus = "Hiatus"


class Novel(Box):
    def __init__(
        self,
        url: str,
        title: str,
        authors: List[str] = [],
        cover_url: Optional[str] = None,
        chapters: List[Chapter] = [],
        volumes: List[Volume] = [],
        is_rtl: Optional[bool] = None,
        synopsis: Optional[str] = None,
        language: Optional[str] = None,
        novel_tags: List[str] = [],
        has_manga: Optional[bool] = None,
        has_mtl: Optional[bool] = None,
        language_code: List[str] = [],
        source: Optional[str] = None,
        editors: List[str] = [],
        translators: List[str] = [],
        status: Optional[NovelStatus] = NovelStatus.unknown,
        genres: List[str] = [],
        tags: List[str] = [],
        description: Optional[str] = None,
        original_publisher: Optional[str] = None,
        english_publisher: Optional[str] = None,
        novelupdates_url: Optional[str] = None,
        **kwargs,
    ) -> None:
        self.url = url
        self.title = title
        self.authors = authors
        self.cover_url = cover_url
        self.chapters = chapters
        self.volumes = volumes
        self.is_rtl = is_rtl
        self.synopsis = synopsis
        self.language = language
        self.novel_tags = novel_tags
        self.has_manga = has_manga
        self.has_mtl = has_mtl
        self.language_code = language_code
        self.source = source
        self.editors = editors
        self.translators = translators
        self.status = status
        self.genres = genres
        self.tags = tags
        self.description = description
        self.original_publisher = original_publisher
        self.english_publisher = english_publisher
        self.novelupdates_url = novelupdates_url
        self.update(kwargs)

    @property
    def language(self) -> str:
        return language_codes.get(self.language_code, "Unknown")
