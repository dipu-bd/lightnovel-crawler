from __future__ import annotations

import threading
import time


class CloudscraperSessionState:
    """Thread-safe container for CloudScraper's mutable per-session counters.

    All compound read-modify-write operations are performed under a single lock so
    the scraper can be driven from multiple threads (e.g. an abort thread) safely.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._session_start = time.monotonic()
        self._last_request = 0.0
        self._cf_active = False
        self._retry_403 = 0
        self._last_403 = 0.0
        self._cipher_rotations = 0

    @property
    def cf_active(self) -> bool:
        with self._lock:
            return self._cf_active

    def mark_cf_active(self) -> None:
        with self._lock:
            self._cf_active = True

    def throttle_delay(self, fast: float, slow: float) -> float:
        """Seconds to sleep to honour the min interval for the current CF state."""
        with self._lock:
            interval = slow if self._cf_active else fast
            return max(0.0, interval - (time.monotonic() - self._last_request))

    def mark_request_sent(self) -> None:
        with self._lock:
            self._last_request = time.monotonic()

    def next_cipher_rotation(self) -> int:
        with self._lock:
            self._cipher_rotations += 1
            return self._cipher_rotations

    def needs_refresh(self, max_age: float) -> bool:
        with self._lock:
            now = time.monotonic()
            recent_403 = self._last_403 > 0 and (now - self._last_403) < 60
            return (now - self._session_start) > max_age or recent_403

    def reset_session_clock(self) -> None:
        with self._lock:
            self._session_start = time.monotonic()

    def reset_403(self) -> None:
        with self._lock:
            self._retry_403 = 0
            self._last_403 = 0.0

    def register_403(self, limit: int) -> bool:
        """Record a 403 retry attempt; return True if still under *limit*."""
        with self._lock:
            if self._retry_403 >= limit:
                return False
            self._retry_403 += 1
            self._last_403 = time.monotonic()
            return True
