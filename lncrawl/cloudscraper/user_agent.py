"""User-Agent selection for CloudScraper.

On first use, fetches a current UA dataset from intoli/user-agents (GitHub raw),
caches it locally with ETag-based validation so re-downloads only happen when the
upstream file actually changes, and filters to modern browser versions (≥ 120).
Falls back to an embedded generator when the network is unavailable.
"""

from __future__ import annotations

from collections import OrderedDict
import gzip
import json
import logging
from pathlib import Path
import random
import re
import tempfile
import time
from typing import Dict

logger = logging.getLogger(__name__)

# ------------------------------------------------------------------------------- #
# Remote data source
# ------------------------------------------------------------------------------- #

_CACHE_URL = "https://raw.githubusercontent.com/intoli/user-agents/main/src/user-agents.json.gz"
_CACHE_PATH = Path(tempfile.gettempdir()) / "lncrawl_ua_cache.json.gz"
_ETAG_PATH = Path(tempfile.gettempdir()) / "lncrawl_ua_cache.etag"
_FAST_TTL = 3600  # seconds — skip network entirely if cache is this fresh

# ------------------------------------------------------------------------------- #
# Browser / platform constants
# ------------------------------------------------------------------------------- #

_BROWSERS = ["chrome", "firefox"]
_PLATFORMS = ["windows", "darwin", "linux", "android", "ios"]

# ------------------------------------------------------------------------------- #
# Embedded cipher suites and headers (from the original browsers.json — accurate)
# ------------------------------------------------------------------------------- #

_CIPHER_SUITES: Dict[str, list[str]] = {
    "chrome": [
        "TLS_AES_128_GCM_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-RSA-AES256-SHA",
        "AES128-GCM-SHA256",
        "AES256-GCM-SHA384",
        "AES128-SHA",
        "AES256-SHA",
        "DES-CBC3-SHA",
    ],
    "firefox": [
        "TLS_AES_128_GCM_SHA256",
        "TLS_CHACHA20_POLY1305_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "ECDHE-ECDSA-AES128-GCM-SHA256",
        "ECDHE-RSA-AES128-GCM-SHA256",
        "ECDHE-ECDSA-CHACHA20-POLY1305",
        "ECDHE-RSA-CHACHA20-POLY1305",
        "ECDHE-ECDSA-AES256-GCM-SHA384",
        "ECDHE-RSA-AES256-GCM-SHA384",
        "ECDHE-ECDSA-AES256-SHA",
        "ECDHE-ECDSA-AES128-SHA",
        "ECDHE-RSA-AES128-SHA",
        "ECDHE-RSA-AES256-SHA",
        "DHE-RSA-AES128-SHA",
        "DHE-RSA-AES256-SHA",
        "AES128-SHA",
        "AES256-SHA",
        "DES-CBC3-SHA",
    ],
}

_HEADERS: Dict[str, dict] = {
    "chrome": {
        "User-Agent": None,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    },
    "firefox": {
        "User-Agent": None,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
    },
}

# ------------------------------------------------------------------------------- #
# Fallback UA generator (used when download fails or filtered set is empty)
# ------------------------------------------------------------------------------- #

_CHROME_VERSIONS = list(range(140, 149))
_FIREFOX_VERSIONS = list(range(140, 152))
_ANDROID_VERSIONS = list(range(12, 18))
_IOS_VERSIONS = ["16_0", "16_6", "17_0", "17_4", "18_0", "26_5"]
_MAC_VERSIONS = ["10_15_7", "11_0", "12_0", "13_0_0", "14_0_0", "15_7_7", "26_5_1"]
_ANDROID_DEVICES = ["Pixel 7", "Pixel 8", "Pixel 8 Pro", "SM-S911B", "SM-S918B"]


def _generate_ua_fallback(browser: str, platform: str, rng: random.Random) -> str:
    """Generate a realistic modern UA string without any network or disk I/O."""
    if browser == "firefox":
        v = rng.choice(_FIREFOX_VERSIONS)
        if platform == "windows":
            return (
                f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
            )
        if platform == "darwin":
            mac = rng.choice(_MAC_VERSIONS)
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac}; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
        if platform == "android":
            av = rng.choice(_ANDROID_VERSIONS)
            return f"Mozilla/5.0 (Android {av}; Mobile; rv:{v}.0) Gecko/{v}.0 Firefox/{v}.0"
        if platform == "ios":
            iv = rng.choice(_IOS_VERSIONS)
            return (
                f"Mozilla/5.0 (iPhone; CPU iPhone OS {iv} like Mac OS X) "
                f"AppleWebKit/605.1.15 (KHTML, like Gecko) FxiOS/{v}.0 Mobile/15E148 Safari/605.1.15"
            )
        # linux (default)
        return f"Mozilla/5.0 (X11; Linux x86_64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0"
    else:
        # chrome
        v = rng.choice(_CHROME_VERSIONS)
        webkit = "AppleWebKit/537.36 (KHTML, like Gecko)"
        if platform == "darwin":
            mac = rng.choice(_MAC_VERSIONS)
            return f"Mozilla/5.0 (Macintosh; Intel Mac OS X {mac}) {webkit} Chrome/{v}.0.0.0 Safari/537.36"
        if platform == "linux":
            return f"Mozilla/5.0 (X11; Linux x86_64) {webkit} Chrome/{v}.0.0.0 Safari/537.36"
        if platform == "android":
            av = rng.choice(_ANDROID_VERSIONS)
            device = rng.choice(_ANDROID_DEVICES)
            return (
                f"Mozilla/5.0 (Linux; Android {av}; {device}) "
                f"{webkit} Chrome/{v}.0.0.0 Mobile Safari/537.36"
            )
        if platform == "ios":
            iv = rng.choice(_IOS_VERSIONS)
            return (
                f"Mozilla/5.0 (iPhone; CPU iPhone OS {iv} like Mac OS X) "
                f"AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/{v}.0.0.0 Mobile/15E148 Safari/604.1"
            )
        # windows (default)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) {webkit} Chrome/{v}.0.0.0 Safari/537.36"


# ------------------------------------------------------------------------------- #
# Remote UA data: fetch, cache, filter, select
# ------------------------------------------------------------------------------- #


def _read_cache() -> list[dict] | None:
    try:
        with gzip.open(_CACHE_PATH) as f:
            return json.loads(f.read())
    except Exception:
        return None


def _load_ua_data() -> list[dict] | None:
    """Return the intoli UA dataset, downloading/validating via ETag as needed."""
    import requests as _req

    # Fast path: cache is fresh — no network call at all.
    if _CACHE_PATH.exists():
        if time.time() - _CACHE_PATH.stat().st_mtime < _FAST_TTL:
            return _read_cache()

    # Conditional GET using stored ETag (avoids re-downloading unchanged data).
    headers: Dict[str, str] = {}
    if _ETAG_PATH.exists():
        headers["If-None-Match"] = _ETAG_PATH.read_text().strip()

    try:
        resp = _req.get(_CACHE_URL, headers=headers, timeout=10)
        if resp.status_code == 304:
            # Unchanged — just reset mtime so fast path applies next time.
            _CACHE_PATH.touch()
            return _read_cache()
        resp.raise_for_status()
        _CACHE_PATH.write_bytes(resp.content)
        if etag := resp.headers.get("ETag"):
            _ETAG_PATH.write_text(etag)
        return _read_cache()
    except Exception:
        logger.debug("UA data fetch failed; trying stale cache or fallback.")
        return _read_cache()  # stale cache beats nothing


_MIN_CHROME = 120
_MIN_FIREFOX = 120


def _infer_platform(ua: str, platform_str: str, device_cat: str) -> str:
    if device_cat == "mobile":
        return "ios" if ("iPhone" in ua or "iPad" in ua) else "android"
    if "Win" in platform_str or "Windows" in ua:
        return "windows"
    if "Mac" in platform_str or "Macintosh" in ua:
        return "darwin"
    return "linux"


def _browser_from_ua(ua: str) -> str:
    return "firefox" if "Firefox/" in ua else "chrome"


def _filter_ua_data(
    data: list[dict],
    browser: str | None,
    platform: str | None,
    desktop: bool,
    mobile: bool,
) -> list[dict]:
    result: list[dict] = []
    for entry in data:
        ua = entry.get("userAgent", "")
        cat = entry.get("deviceCategory", "desktop")
        plat_str = entry.get("platform", "")

        # Browser + version filter
        if "Firefox/" in ua:
            m = re.search(r"Firefox/(\d+)", ua)
            if not m or int(m.group(1)) < _MIN_FIREFOX:
                continue
            entry_browser = "firefox"
        elif "Chrome/" in ua and "Chromium" not in ua:
            m = re.search(r"Chrome/(\d+)", ua)
            if not m or int(m.group(1)) < _MIN_CHROME:
                continue
            entry_browser = "chrome"
        else:
            continue  # skip Edge, Safari, etc.

        if browser and entry_browser != browser:
            continue

        # Device category filter
        is_mobile_entry = cat == "mobile"
        if is_mobile_entry and not mobile:
            continue
        if not is_mobile_entry and not desktop:
            continue

        # Platform filter
        if platform and _infer_platform(ua, plat_str, cat) != platform:
            continue

        result.append(entry)
    return result


def _weighted_choice(entries: list[dict], rng: random.Random) -> dict:
    weights = [e.get("weight", 1e-6) for e in entries]
    total = sum(weights)
    threshold = rng.random() * total
    cumulative = 0.0
    for entry, w in zip(entries, weights):
        cumulative += w
        if cumulative >= threshold:
            return entry
    return entries[-1]


# ------------------------------------------------------------------------------- #
# UserAgent class
# ------------------------------------------------------------------------------- #


class UserAgent:
    """Selects a browser User-Agent and matching TLS cipher suite.

    Attempts to use fresh data from intoli/user-agents (cached locally with ETag
    validation). Falls back to an embedded generator on network failure.
    """

    def __init__(self, allow_brotli: bool = False, browser: dict | None = None) -> None:
        self.headers: OrderedDict = OrderedDict()
        self.cipher_suite: list[str] = []
        self.load(allow_brotli=allow_brotli, browser=browser)

    def load(self, allow_brotli: bool = False, browser: dict | None = None) -> None:
        rng = random.SystemRandom()
        cfg = browser or {}
        if isinstance(cfg, str):
            cfg = {"browser": cfg}

        custom: str | None = cfg.get("custom")
        if custom:
            browser_name = _browser_from_ua(custom)
            self.cipher_suite = list(_CIPHER_SUITES[browser_name])
            self.headers = OrderedDict(_HEADERS[browser_name])
            self.headers["User-Agent"] = custom
        else:
            browser_name = cfg.get("browser") or rng.choice(_BROWSERS)
            desktop: bool = bool(cfg.get("desktop", True))
            mobile: bool = bool(cfg.get("mobile", True))
            platform: str | None = cfg.get("platform") or None

            if browser_name not in _BROWSERS:
                raise RuntimeError(
                    f'Browser "{browser_name}" is not valid. Valid choices: {_BROWSERS}'
                )
            if platform and platform not in _PLATFORMS:
                raise RuntimeError(
                    f'Platform "{platform}" is not valid. Valid choices: {_PLATFORMS}'
                )
            if not desktop and not mobile:
                raise RuntimeError("mobile and desktop cannot both be disabled.")

            ua_str: str | None = None

            data = _load_ua_data()
            if data:
                filtered = _filter_ua_data(data, browser_name, platform, desktop, mobile)
                if filtered:
                    chosen = _weighted_choice(filtered, rng)
                    ua_str = chosen.get("userAgent") or ""
                    browser_name = _browser_from_ua(ua_str)

            if not ua_str:
                eff_platform = platform or rng.choice(_PLATFORMS)
                is_mobile = eff_platform in ("android", "ios")
                if is_mobile and not mobile:
                    eff_platform = rng.choice(["windows", "darwin", "linux"])
                    is_mobile = False
                elif not is_mobile and not desktop:
                    eff_platform = rng.choice(["android", "ios"])
                    is_mobile = True
                ua_str = _generate_ua_fallback(browser_name, eff_platform, rng)

            self.cipher_suite = list(_CIPHER_SUITES[browser_name])
            self.headers = OrderedDict(_HEADERS[browser_name])
            self.headers["User-Agent"] = ua_str

        if not allow_brotli and "br" in self.headers.get("Accept-Encoding", ""):
            self.headers["Accept-Encoding"] = ", ".join(
                enc.strip()
                for enc in self.headers["Accept-Encoding"].split(",")
                if enc.strip() != "br"
            )
