from typing import List

from box import Box


class SearchResult(Box):
    def __init__(
        self,
        title: str,
        url: str,
        info: str = "",
    ) -> None:
        self.title = title
        self.url = url
        self.info = info


class CombinedSearchResult(Box):
    def __init__(
        self,
        id: str,
        title: str,
        novels: List[SearchResult] = [],
    ) -> None:
        self.id = id
        self.title = title
        self.novels = novels
