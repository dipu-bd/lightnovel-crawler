from typing import List, Optional

from box import Box

from ..assets.languages import find_code
from .chapter import Chapter
from .volume import Volume


class Novel(Box):
    def __init__(
        self,
        url: str,
        title: str,
        authors: List[str] = [],
        cover_url: Optional[str] = None,
        chapters: List[Chapter] = [],
        volumes: List[Volume] = [],
        is_rtl: bool = False,
        synopsis: str = "",
        language: Optional[str] = None,
        tags: List[str] = [],
        has_manga: Optional[bool] = None,
        has_mtl: Optional[bool] = None,
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
        self.has_manga = has_manga
        self.has_mtl = has_mtl
        self.language = find_code(language)
        self.tags = tags
        self.update(kwargs)
