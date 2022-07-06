from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus
from typing import Any, List, Optional

@dataclass(init=False)
class _Novel:
    title: str = ""
    path: Optional[Path] = None
    cover: Optional[str] = None
    author: str = ""
    chapter_count: int = 0
    volume_count: int = 0
    slug: str = ""
    first: str = ""
    latest: str = ""
    summary: str = ""
    language: str = "en"

    def __init__(self, path: Path):
        self.path = path
        self.slug = quote_plus(path.name)

    def __hash__(self) -> int:
        return super().__hash__()


@dataclass(init=False)
class Novel(_Novel):
    """
    Holds information about a novel.
    """
    prefered_source: Optional[NovelFromSource] = None
    source_count: int = 0
    clicks : int = 0
    overall_rating: float = 0.0
    ratings_count = property(lambda self: len(self.ratings))
    rank:int

    def __init__(self, path: Path):
        self.search_words = []
        self.sources = []
        self.ratings: dict[str, int] = {}
        self.search_words: List[str] = []
        self.sources: list[NovelFromSource] = []

        super().__init__(path)

    def __eq__(self, other: Any) -> bool:
        """
        Overrides the default implementation
        _Novel are equal if they have the same title
        """
        if issubclass(type(other), _Novel):
            return self.title == other.title
        return False

    def __hash__(self) -> int:
        """Overrides the default implementation"""
        return hash(self.title)


@dataclass(init=False)
class NovelFromSource(_Novel):
    """
    Hold information about a novel from a source.
    """

    novel: Novel
