from hashlib import md5
import logging
import random
from threading import Event
from typing import Optional

from ...context import ctx
from .backend_base import ChunkedBackendBase
from .languages import LanguageCode

logger = logging.getLogger(__name__)

# Baidu uses non-standard codes for some languages
# https://machinetranslate.org/baidu#language-support
_LANG_MAP = {
    LanguageCode.ar: "ara",
    LanguageCode.bn: "ben",
    LanguageCode.de: "de",
    LanguageCode.en: "en",
    LanguageCode.es: "spa",
    LanguageCode.fr: "fra",
    LanguageCode.hi: "hin",
    LanguageCode.id: "ind",
    LanguageCode.ja: "jpn",
    LanguageCode.ko: "kor",
    LanguageCode.pt: "pt-pt",
    LanguageCode.ru: "ru",
    LanguageCode.ur: "urd",
    LanguageCode.vi: "vie",
    LanguageCode.zh_cn: "zh",
    LanguageCode.zh_tw: "cht",
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
