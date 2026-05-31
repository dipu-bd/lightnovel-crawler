import json
import logging
from threading import Event
import time
from typing import Iterable, Optional

from ...enums import LanguageCode
from .backend_base import BackendBase

logger = logging.getLogger(__name__)

_TOKEN_TTL = 480  # Edge tokens live ~10 minutes; refresh at 8

# https://learn.microsoft.com/en-us/azure/ai-services/translator/language-support
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
    LanguageCode.chinese_simplified: "zh-Hans",
    LanguageCode.chinese_traditional: "zh-Hant",
}


class BingTranslate(BackendBase):
    def __init__(
        self,
        max_workers: int = 1,
        ratelimit: Optional[float] = None,
    ) -> None:
        super().__init__(max_workers, ratelimit)
        self._token: str = ""
        self._token_expiry: float = 0.0

    def is_enabled(self, language: LanguageCode) -> bool:
        return language in _LANG_MAP

    def _get_token(self) -> str:
        if time.monotonic() < self._token_expiry:
            return self._token
        self._token = self.scraper.get(
            "https://edge.microsoft.com/translate/auth",
            timeout=30,
        ).text.strip()
        self._token_expiry = time.monotonic() + _TOKEN_TTL
        return self._token

    def translate_batch(
        self,
        texts: Iterable[str],
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> Iterable[str]:
        if target not in _LANG_MAP:
            raise ValueError(f"Bing Translate does not support: {target}")
        with self.lock:
            if signal is not None:
                self.scraper.signal = signal
            data = self.scraper.post_json(
                "https://api.cognitive.microsofttranslator.com/translate",
                data=json.dumps([{"Text": t} for t in texts]),
                headers={"Authorization": f"Bearer {self._get_token()}"},
                params={"api-version": "3.0", "to": _LANG_MAP[target]},
                timeout=60,
            )
        return (item["translations"][0]["text"] for item in data)
