from typing import Any, Dict, List, Optional

from box import Box

__all__ = [
    "Novel",
    "Volume",
    "Chapter",
    "SearchResult",
    "CombinedSearchResult",
]


_keys_ = "__model_keys__"


class Chapter(Box):
    def __init__(
        self,
        id: int,
        url: str = "",
        title: str = "",
        volume: Optional[int] = None,
        body: Optional[str] = None,
        images: Dict[str, str] = dict(),
        success: bool = False,
        crawler_version: Optional[int] = None,
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.volume = volume
        self.body = body
        self.images = images
        self.success = success
        self.crawler_version = crawler_version
        self[_keys_] = set(self.keys())
        self.update(kwargs)


class Volume(Box):
    def __init__(
        self,
        id: int,
        title: str = "",
        chapters: int = 0,
        crawler_version: Optional[int] = None,
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.title = title
        self.chapters = chapters
        self.crawler_version = crawler_version
        self[_keys_] = set(self.keys())
        self.update(kwargs)


class Novel(Box):
    def __init__(
        self,
        url: str,
        title: Optional[str] = None,
        cover_url: Optional[str] = None,
        volumes: Optional[List[Volume]] = None,
        chapters: Optional[List[Chapter]] = None,
        author: Optional[str] = None,
        synopsis: Optional[str] = None,
        tags: Optional[List[str]] = None,
        language: Optional[str] = None,
        is_manga: Optional[bool] = None,
        is_mtl: Optional[bool] = None,
        is_rtl: Optional[bool] = None,
        crawler_version: Optional[int] = None,
        **kwargs,
    ) -> None:
        self.url = url
        self.title = title
        self.cover_url = cover_url
        self.volumes = volumes
        self.chapters = chapters
        self.author = author
        self.synopsis = synopsis
        self.tags = tags
        self.language = language
        self.is_manga = is_manga
        self.is_mtl = is_mtl
        self.is_rtl = is_rtl
        self.crawler_version = crawler_version
        self[_keys_] = set(self.keys())
        self.update(kwargs)


class SearchResult(Box):
    def __init__(
        self,
        title: str,
        url: str,
        info: str = "",
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.title = str(title)
        self.url = str(url)
        self.info = str(info)
        self[_keys_] = set(self.keys())
        self.update(kwargs)


class CombinedSearchResult(Box):
    def __init__(
        self,
        id: str,
        title: str,
        novels: List[SearchResult] = [],
        extras: Dict[str, Any] = dict(),
        **kwargs,
    ) -> None:
        self.id = id
        self.title = str(title)
        self.novels = novels
        self[_keys_] = set(self.keys())
        self.update(kwargs)


def get_extras(obj: Box) -> Dict[str, Any]:
    """Get all extra fields from a Box object"""
    if _keys_ not in obj:
        return {}
    extra_keys = obj.keys() - obj[_keys_] - {_keys_}
    return {k: obj[k] for k in extra_keys}
