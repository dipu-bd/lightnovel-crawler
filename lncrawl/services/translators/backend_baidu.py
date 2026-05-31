from hashlib import md5
import logging
import random
from threading import Event
from typing import Optional

from ...context import ctx
from ...enums import LanguageCode
from .backend_base import ChunkedBackendBase

logger = logging.getLogger(__name__)

# Baidu uses non-standard codes for some languages
# https://machinetranslate.org/baidu#language-support
_LANG_MAP = {
    LanguageCode.arabic: "ara",
    LanguageCode.bangla: "ben",
    LanguageCode.german: "de",
    LanguageCode.english: "en",
    LanguageCode.spanish: "spa",
    LanguageCode.french: "fra",
    LanguageCode.hindi: "hin",
    LanguageCode.indonesian: "ind",
    LanguageCode.japanese: "jpn",
    LanguageCode.korean: "kor",
    LanguageCode.portuguese: "pt-pt",
    LanguageCode.russian: "ru",
    LanguageCode.thai: "tha",
    LanguageCode.turkish: "tur",
    LanguageCode.urdu: "urd",
    LanguageCode.vietnamese: "vie",
    LanguageCode.chinese: "zh",
    LanguageCode.chinese_simplified: "zh",
    LanguageCode.chinese_traditional: "cht",
}


class BaiduTranslate(ChunkedBackendBase):
    def is_enabled(self, language: LanguageCode) -> bool:
        return bool(
            language in _LANG_MAP
            and ctx.config.translator.baidu_app_id
            and ctx.config.translator.baidu_secret_key
        )

    def translate(
        self,
        text: str,
        target: LanguageCode,
        signal: Optional[Event] = None,
    ) -> str:
        app_id = ctx.config.translator.baidu_app_id
        secret_key = ctx.config.translator.baidu_secret_key
        if not app_id or not secret_key:
            raise ValueError("Baidu Translate credentials are not configured")
        if target not in _LANG_MAP:
            raise ValueError(f"Baidu Translate does not support: {target}")

        salt = str(random.randint(10000, 99999))
        sign = md5(f"{app_id}{text}{salt}{secret_key}".encode()).hexdigest()

        with self.lock:
            if signal is not None:
                self.scraper.signal = signal
            data = self.scraper.get_json(
                "https://fanyi-api.baidu.com/api/trans/vip/translate",
                params={
                    "q": text,
                    "from": "auto",
                    "to": _LANG_MAP[target],
                    "appid": app_id,
                    "salt": salt,
                    "sign": sign,
                },
                timeout=60,
            )

        if "error_code" in data:
            raise ValueError(f"Baidu error {data['error_code']}: {data.get('error_msg', '')}")
        return "".join(r["dst"] for r in data["trans_result"])
