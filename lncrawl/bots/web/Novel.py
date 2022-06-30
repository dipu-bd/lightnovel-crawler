from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote_plus
from typing import List

@dataclass(init=False)
class _Novel:
    title: str = ""
    path: Path = None
    cover: Path = None
    author: str = ""
    chapter_count: int = 0
    volume_count: int = 0
    slug: str = ""
    first: str = ""
    latest: str = ""
    summary: str = ""
    language : str = 'en'

    def __init__(self, path: Path):
        self.path = path
        self.slug = quote_plus(path.name)

@dataclass(init=False)
class Novel(_Novel):
    """
    Holds information about a novel.
    """
    sources: list['NovelFromSource']
    prefered_source : 'NovelFromSource' = None
    source_count: int = 0
    search_words: List[str] 

    def __init__(self, path: Path):
        self.search_words = []
        self.sources = []
        super().__init__(path)

    def __eq__(self, other):
        """
        Overrides the default implementation
        _Novel are equal if they have the same title
        """
        if issubclass(type(other), _Novel):
            return self.title == other.title
        return False


    def __hash__(self):
        """Overrides the default implementation"""
        return hash(self.title)


@dataclass(init=False)
class NovelFromSource(_Novel):
    """
    Hold information about a novel from a source.
    """
    novel: Novel