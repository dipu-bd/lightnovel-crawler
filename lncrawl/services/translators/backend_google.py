import logging
from threading import Event
from typing import Optional

from .backend_base import ChunkedBackendBase
from .languages import LanguageCode

logger = logging.getLogger(__name__)


class GoogleMobileTranslate(ChunkedBackendBase):
    def is_enabled(self, language: LanguageCode) -> bool:
        return True  # no API key required

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            self.scraper.signal = signal
            soup = self.scraper.get_soup(
                "https://translate.google.com/m",
                params={
                    "sl": "auto",
                    "tl": target,
                    "q": text,
                },
                timeout=60,
            )
            result = soup.select_one("div.result-container")
            if not result:
                raise ValueError("No result in Google mobile response")
            return result.get_text()


class GoogleClient5Translate(ChunkedBackendBase):
    def is_enabled(self, language: LanguageCode) -> bool:
        return True  # no API key required

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            self.scraper.signal = signal
            data = self.scraper.get_json(
                "https://clients5.google.com/translate_a/t",
                params={
                    "client": "dict-chrome-ex",
                    "sl": "auto",
                    "tl": target,
                    "q": text,
                },
                timeout=60,
            )
            return "".join(part[0] for part in data if part[0])


class GoogleGtxTranslate(ChunkedBackendBase):
    def is_enabled(self, language: LanguageCode) -> bool:
        return True  # no API key required

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            self.scraper.signal = signal
            data = self.scraper.get_json(
                "https://translate.googleapis.com/translate_a/single",
                params={
                    "client": "gtx",
                    "dt": "t",
                    "sl": "auto",
                    "tl": target,
                    "q": text,
                },
                timeout=60,
            )
            return "".join(part[0] for part in data[0] if part[0])
