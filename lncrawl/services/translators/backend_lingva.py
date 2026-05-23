import logging
from threading import Event
from typing import Optional
from urllib.parse import quote

from .backend_base import ChunkedBackendBase
from .languages import LanguageCode

logger = logging.getLogger(__name__)


class LingvaTranslate(ChunkedBackendBase):
    """Calls Google Mobile translate API internally."""

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
                f"https://lingva.ml/api/v1/auto/{target}/{quote(text, safe='')}",
                timeout=60,
            )
            return data["translation"]
