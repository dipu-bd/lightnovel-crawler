import logging
from threading import Event
from typing import Optional
from urllib.parse import quote

from ...enums import LanguageCode
from .backend_base import ChunkedBackendBase
from .backend_google import _LANG_MAP

logger = logging.getLogger(__name__)


class LingvaTranslate(ChunkedBackendBase):
    """Calls Google Mobile translate API internally."""

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
                f"https://lingva.ml/api/v1/auto/{target}/{quote(text, safe='')}",
                timeout=60,
            )
            return data["translation"]
