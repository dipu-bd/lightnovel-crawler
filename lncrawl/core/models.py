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
        title: str = "",
        cover_url: str = "",
        volumes: List[Volume] = [],
        chapters: List[Chapter] = [],
        author: str = "",
        synopsis: str = "",
        tags: List[str] = [],
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

    def add_volume(
        self,
        id: Optional[int] = None,
        title: str = "",
        **kwargs,
    ) -> Volume:
        if id is None:
            id = len(self.volumes) + 1
        volume = Volume(
            id=id,
            title=title,
            crawler_version=self.crawler_version,
            **kwargs,
        )
        self.volumes.append(volume)
        return volume

    def add_chapter(
        self,
        id: Optional[int] = None,
        url: str = "",
        title: str = "",
        volume: Optional[int] = None,
        **kwargs,
    ) -> Chapter:
        if id is None:
            id = len(self.chapters) + 1
        chapter = Chapter(
            id=id,
            url=url,
            title=title,
            volume=volume,
            crawler_version=self.crawler_version,
            **kwargs,
        )
        self.chapters.append(chapter)
        return chapter


class SearchResult(Box):
    def __init__(
        self,
        title: str,
        url: str,
        info: str = "",
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
