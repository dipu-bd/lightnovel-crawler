from datetime import date, datetime
from typing import Any, Dict, List, Optional

from box import Box
from pydantic import BaseModel

__all__ = [
    "Novel",
    "Volume",
    "Chapter",
    "SearchResult",
    "CombinedSearchResult",
]


_keys_ = "__model_keys__"


def _json_safe(v: Any, _seen=set()) -> Any:
    if isinstance(v, (str, int, float, bool)) or v is None:
        return v
    if isinstance(v, (datetime, date)):
        return v.isoformat()

    vid = id(v)
    if vid in _seen:
        return None
    _seen.add(vid)

    try:
        if isinstance(v, (list, tuple, set, frozenset)):
            return [_json_safe(i, _seen) for i in v]
        elif isinstance(v, BaseModel):
            return v.model_dump()
        elif isinstance(v, _ModelBox):
            out = v.get_original()
            out["extra"] = v.get_extras()
            return _json_safe(out, _seen)
        elif isinstance(v, Box):
            return _json_safe(v.to_dict(), _seen)
        elif isinstance(v, dict):
            out = dict()
            for k, val in v.items():
                if not callable(v) and not k.startswith("__"):
                    v = _json_safe(val, _seen)
                    if v or isinstance(v, (int, float, bool)):
                        out[k] = v
            return out
        else:
            return str(v)
    finally:
        _seen.discard(vid)


class _ModelBox(Box):
    def __new__(cls, *args: Any, **kwargs: Any):
        obj = super().__new__(cls, *args, **kwargs)
        existing = obj._box_config.get("box_intact_types", ())
        if _ModelBox not in existing:
            obj._box_config["box_intact_types"] = existing + (_ModelBox,)
        return obj

    def __init__(self, **kwargs: Any) -> None:
        _original = list(self.keys())
        self[_keys_] = _original
        self.update(**kwargs)

    def to_dict(self) -> Dict:
        return _json_safe(self)

    def get_original(self) -> Dict[str, Any]:
        if _keys_ not in self:
            return {}
        return {k: self[k] for k in self[_keys_]}

    def get_extras(self) -> Dict[str, Any]:
        keys = set(self.keys())
        if _keys_ not in keys:
            return {}
        keys -= set(self[_keys_])
        keys.discard(_keys_)
        return {k: self[k] for k in keys}


class SearchResult(_ModelBox):
    def __init__(
        self,
        title: str,
        url: str,
        info: str = "",
        **kwargs: Any,
    ) -> None:
        self.title = str(title)
        self.url = str(url)
        self.info = str(info)
        super().__init__(**kwargs)


class CombinedSearchResult(_ModelBox):
    def __init__(
        self,
        id: str,
        title: str,
        novels: List[SearchResult] = [],
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.title = str(title)
        self.novels = novels
        super().__init__(**kwargs)


class Chapter(_ModelBox):
    def __init__(
        self,
        id: int,
        url: str = "",
        title: str = "",
        volume: Optional[int] = None,
        body: Optional[str] = None,
        images: Dict[str, str] = dict(),
        success: bool = False,
        crawler_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.volume = volume
        self.body = body
        self.images = images
        self.success = success
        self.crawler_version = crawler_version
        super().__init__(**kwargs)


class Volume(_ModelBox):
    def __init__(
        self,
        id: int,
        title: str = "",
        chapters: int = 0,
        crawler_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.id = id
        self.title = title
        self.chapters = chapters
        self.crawler_version = crawler_version
        super().__init__(**kwargs)


class Novel(_ModelBox):
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
        crawler_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        self.crawler_version = crawler_version
        self.url = url
        self.title = title
        self.cover_url = cover_url
        self.author = author
        self.language = language
        self.is_manga = is_manga
        self.is_mtl = is_mtl
        self.is_rtl = is_rtl
        self.tags = tags
        self.synopsis = synopsis
        self.volumes = volumes
        self.chapters = chapters
        super().__init__(**kwargs)

    def add_volume(
        self,
        id: Optional[int] = None,
        title: str = "",
        **kwargs: Any,
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
        **kwargs: Any,
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
