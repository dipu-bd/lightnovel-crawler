from typing import Dict, Optional

from box import Box


class Chapter(Box):
    def __init__(
        self,
        id: int,
        url: str = "",
        title: str = "",
        volume: Optional[int] = None,
        volume_title: Optional[str] = None,
        body: Optional[str] = None,
        images: Dict[str, str] = dict(),
        success: bool = False,
        **kwargs,
    ) -> None:
        self.id = id
        self.url = url
        self.title = title
        self.volume = volume
        self.volume_title = volume_title
        self.body = body
        self.images = images
        self.success = success
        self.update(kwargs)

    @staticmethod
    def without_body(item: "Chapter") -> "Chapter":
        result = item.copy()
        result.body = None
        return result
