from __future__ import annotations

import logging
import socket
import threading
import time
from typing import Dict

from .config import ProxyConfig

logger = logging.getLogger(__name__)

ProxyDict = Dict[str, str]

# Minimum seconds between consecutive identity rotations (debounce).
_ROTATE_COOLDOWN = 10.0


class ProxyManager:
    """Round-robin proxy selector for Docker-based SOCKS/HTTP proxies.

    Intended for use with containers like peterdavehello/tor-socks-proxy
    (``socks5://127.0.0.1:9150``). Multiple URLs are cycled in order.
    Call ``rotate_identity()`` to request a new Tor exit circuit via the
    control port (SIGNAL NEWNYM); it is called automatically on proxy errors.
    """

    def __init__(self, config: ProxyConfig | None = None) -> None:
        cfg = config or ProxyConfig()
        self._urls = [p.strip() for p in cfg.proxy_urls if p and p.strip()]
        self._control_host = cfg.tor_control_host
        self._control_port = cfg.tor_control_port
        self._control_password = cfg.tor_control_password
        self._index = 0
        self._lock = threading.Lock()
        self._last_rotate = 0.0
        if self._urls:
            logger.debug("ProxyManager: %d proxy URL(s) configured.", len(self._urls))

    @property
    def has_proxy(self) -> bool:
        return bool(self._urls)

    def get_proxy(self) -> ProxyDict | None:
        with self._lock:
            if not self._urls:
                return None
            url = self._urls[self._index % len(self._urls)]
            self._index += 1
        if "://" not in url:
            raise ValueError(f"No scheme in proxy URL: {url}")
        return {"http": url, "https": url}

    def rotate_identity(self) -> None:
        """Request a new Tor exit circuit via the control port (SIGNAL NEWNYM).

        Blocks ~5 s while Tor builds the new circuit. Debounced to at most
        once every ``_ROTATE_COOLDOWN`` seconds across threads. No-op when
        ``tor_control_port`` is 0.
        """
        if not self._control_port:
            return
        now = time.monotonic()
        with self._lock:
            if now - self._last_rotate < _ROTATE_COOLDOWN:
                return
            self._last_rotate = now
        try:
            with socket.create_connection(
                (self._control_host, self._control_port), timeout=10
            ) as s:
                s.sendall(f'AUTHENTICATE "{self._control_password}"\r\n'.encode())
                resp = s.recv(128)
                if not resp.startswith(b"250"):
                    raise RuntimeError(f"Tor control auth failed: {resp.decode()!r}")
                s.sendall(b"SIGNAL NEWNYM\r\n")
                resp = s.recv(128)
                if not resp.startswith(b"250"):
                    raise RuntimeError(f"NEWNYM rejected: {resp.decode()!r}")
            logger.debug("Tor identity rotated — waiting for new circuit.")
            time.sleep(5)
        except Exception as exc:
            logger.warning("Tor identity rotation failed: %s", exc)
