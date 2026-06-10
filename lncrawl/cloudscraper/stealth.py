from __future__ import annotations

from collections import OrderedDict
import logging
import random
import time
from typing import Any, Dict

from .config import StealthConfig

logger = logging.getLogger(__name__)

_CHROME_QUIRKS: Dict[str, Any] = {
    "order": [
        "Host",
        "Connection",
        "sec-ch-ua",
        "sec-ch-ua-mobile",
        "sec-ch-ua-platform",
        "User-Agent",
        "Accept",
        "Sec-Fetch-Site",
        "Sec-Fetch-Mode",
        "Sec-Fetch-User",
        "Sec-Fetch-Dest",
        "Referer",
        "Accept-Encoding",
        "Accept-Language",
        "Cookie",
    ],
    "headers": {
        "sec-ch-ua": '"Google Chrome";v="117", "Not;A=Brand";v="8", "Chromium";v="117"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "?1",
        "Sec-Fetch-Dest": "document",
        "Accept-Language": "en-US,en;q=0.9",
    },
}

_FIREFOX_QUIRKS: Dict[str, Any] = {
    "order": [
        "Host",
        "User-Agent",
        "Accept",
        "Accept-Language",
        "Accept-Encoding",
        "Connection",
        "Upgrade-Insecure-Requests",
        "Referer",
        "Cookie",
    ],
    "headers": {
        "Accept": (
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        ),
        "Accept-Language": "en-US,en;q=0.5",
        "Upgrade-Insecure-Requests": "1",
        "Connection": "keep-alive",
    },
}

_ACCEPTS = [
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
]

_LANGUAGES = [
    "en-US,en;q=0.9",
    "en-US,en;q=0.8",
    "en-GB,en;q=0.9,en-US;q=0.8",
    "en-CA,en;q=0.9,en-US;q=0.8",
    "en-AU,en;q=0.9,en-US;q=0.8",
]


class StealthMode:
    """Stateless stealth helper — no back-reference to CloudScraper.

    Receives only what it needs at call time via apply().
    """

    def __init__(self, config: StealthConfig) -> None:
        self._config = config
        self._request_count = 0

    def apply(
        self,
        method: str,
        url: str,
        *,
        cf_active: bool = False,
        headers: dict | None = None,
        **kwargs,
    ) -> dict:
        """Apply stealth techniques and return updated kwargs.

        Args:
            method: HTTP method (unused currently, reserved for future per-method logic).
            url: Request URL (unused currently, reserved for future per-host logic).
            cf_active: Whether Cloudflare protection has been detected for this session.
                       Controls which delay range is used.
            headers: Current request headers dict (merged into kwargs['headers']).
            **kwargs: Remaining request kwargs passed through.
        """
        headers = dict(headers or {})

        if self._config.human_like_delays:
            self._apply_delay(cf_active)

        if self._config.randomize_headers:
            headers = self._randomize_headers(headers)

        if self._config.browser_quirks:
            headers = self._apply_browser_quirks(headers)

        self._request_count += 1
        kwargs["headers"] = headers
        return kwargs

    def _apply_delay(self, cf_active: bool) -> None:
        if self._request_count == 0:
            return

        if cf_active:
            delay = random.uniform(self._config.min_delay, self._config.max_delay)
        else:
            delay = random.uniform(self._config.min_delay_fast, self._config.max_delay_fast)

        if cf_active and random.random() < 0.1:
            delay = min(delay * 1.5, 10.0)

        if delay >= 0.05:
            logger.debug("Stealth delay: %.2fs (cf_active=%s)", delay, cf_active)
            time.sleep(delay)

    def _randomize_headers(self, headers: dict) -> dict:
        if "Accept" not in headers:
            headers["Accept"] = random.choice(_ACCEPTS)
        if "Accept-Language" not in headers:
            headers["Accept-Language"] = random.choice(_LANGUAGES)
        if random.random() < 0.5:
            headers["DNT"] = "1"
        return headers

    def _apply_browser_quirks(self, headers: dict) -> dict:
        ua = headers.get("User-Agent", "")
        quirks = _FIREFOX_QUIRKS if "Firefox/" in ua else _CHROME_QUIRKS

        for header, value in quirks["headers"].items():
            headers.setdefault(header, value)

        ordered: dict = OrderedDict()
        for name in quirks["order"]:
            if name in headers:
                ordered[name] = headers[name]
        for name, value in headers.items():
            if name not in ordered:
                ordered[name] = value

        return ordered
