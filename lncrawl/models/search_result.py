from typing import List

from box import Box


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
        self.update(kwargs)
