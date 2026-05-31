from abc import ABC, abstractmethod
from threading import Event
from typing import Generator, Iterable, Optional, Union

from bs4 import BeautifulSoup, Tag

from ...core.scraper import Scraper
from ...core.taskman import TaskManager
from ...enums import LanguageCode
from ...utils.event_lock import EventLock


class BackendBase(ABC):
    def __init__(
        self,
        max_workers: int = 1,
        ratelimit: Optional[float] = None,
    ) -> None:
        self._default_chunk_size = 1000
        self.lock = EventLock()
        self.scraper = Scraper()
        self.taskman = TaskManager(max_workers, ratelimit)

    @property
    def name(self):
        return self.__class__.__name__

    def close(self):
        self.lock.abort()
        self.scraper.close()
        self.taskman.close()

    @abstractmethod
    def is_enabled(self, language: LanguageCode) -> bool:
        return False

    @abstractmethod
    def translate_batch(
        self,
        texts: Iterable[str],
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Iterable[str]:
        raise NotImplementedError()

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        for item in self.translate_batch([text], target, signal):
            return item
        raise RuntimeError("No results")

    def translate_html(
        self,
        html: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Generator[Union[int, str], None, None]:
        soup = BeautifulSoup(html, "html5lib")
        body = soup.find("body")
        assert body  # type checking

        texts = [p.text for p in body.contents]
        total = len(texts)
        yield total

        translations = self.translate_batch(texts, target, signal)
        for i, t in enumerate(translations):
            elem = body.contents[i]
            if isinstance(elem, Tag):
                attrs = " ".join([f'{k}="{v}"' for k, v in elem.attrs.values()])
                yield f"<{elem.name}{' ' if attrs else ''}{attrs}>{t}</{elem.name}>"
            else:
                yield f"<p>{t}</p>"


class ChunkedBackendBase(BackendBase):
    def __init__(
        self,
        max_workers: int = 1,
        chunk_size: int = 4500,
        separator: str = "\r\n\r\n",
        ratelimit: Optional[float] = None,
    ) -> None:
        super().__init__(max_workers, ratelimit)
        self.chunk_size = chunk_size
        self.separator = separator

    def _build(self, texts: Iterable[str]) -> Iterable[str]:
        taken = 0
        current = []
        for text in texts:
            clean = "\n".join(text.split("\r\n"))
            taken += len(clean)
            current.append(clean)
            if taken >= self.chunk_size:
                yield self.separator.join(current)
                taken, current = 0, []
        if taken > 0:
            yield self.separator.join(current)

    def _split(self, chunked_results: Iterable[str]) -> Iterable[str]:
        return (
            text  #
            for result in chunked_results
            for text in result.split(self.separator)
        )

    @abstractmethod
    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        raise NotImplementedError()

    def translate_batch(
        self,
        texts: Iterable[str],
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Iterable[str]:
        futures = (
            self.taskman.submit_task(self.translate, chunk, target, signal)
            for chunk in self._build(texts)
        )
        self.taskman.resolve(
            futures,
            fail_fast=True,
            desc="Translating",
            unit="chunk",
        )
        for out in self._split(f.result() for f in futures):
            yield out
