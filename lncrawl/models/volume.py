from typing import Optional

from box import Box


class Volume(Box):
    def __init__(
        self,
        id: int,
        title: str = "",
        start_chapter: Optional[int] = None,
        final_chapter: Optional[int] = None,
        chapter_count: Optional[int] = None,
        **kwargs,
    ) -> None:
        self.id = id
        self.title = title
        self.start_chapter = start_chapter
        self.final_chapter = final_chapter
        self.chapter_count = chapter_count
        self.update(kwargs)
