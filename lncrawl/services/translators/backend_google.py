import logging
from threading import Event
from typing import Optional

from ...enums import LanguageCode
from .backend_base import ChunkedBackendBase

logger = logging.getLogger(__name__)

# https://docs.cloud.google.com/translate/docs/languages#nmt
_LANG_MAP = {
    LanguageCode.arabic: "ar",
    LanguageCode.bangla: "bn",
    LanguageCode.german: "de",
    LanguageCode.english: "en",
    LanguageCode.spanish: "es",
    LanguageCode.french: "fr",
    LanguageCode.hindi: "hi",
    LanguageCode.indonesian: "id",
    LanguageCode.japanese: "ja",
    LanguageCode.korean: "ko",
    LanguageCode.portuguese: "pt",
    LanguageCode.russian: "ru",
    LanguageCode.thai: "th",
    LanguageCode.turkish: "tr",
    LanguageCode.urdu: "ur",
    LanguageCode.vietnamese: "vi",
    LanguageCode.chinese: "zh",
    LanguageCode.chinese_simplified: "zh-CN",
    LanguageCode.chinese_traditional: "zh-TW",
}


class GoogleMobileTranslate(ChunkedBackendBase):
    def is_enabled(self, language: LanguageCode) -> bool:
        return language in _LANG_MAP

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            if signal is not None:
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
        return language in _LANG_MAP

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            if signal is not None:
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
        return language in _LANG_MAP

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        with self.lock:
            if signal is not None:
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
