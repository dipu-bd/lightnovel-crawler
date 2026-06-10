from __future__ import annotations

import ssl
from typing import Any

from requests.adapters import HTTPAdapter


class CipherRotator:
    """Produces rotating TLS cipher-suite strings from a fixed in-memory pool."""

    _WINDOW = 8

    def __init__(self, ciphers: list[str]) -> None:
        self._pool = list(ciphers or [])

    def suite_for(self, rotation: int) -> str | None:
        """Return a cipher-suite string for the given rotation count, or None to skip."""
        size = len(self._pool)
        if size <= 1:
            return None
        window = min(self._WINDOW, size)
        start = (rotation % size) % max(1, size - window + 1)
        return ":".join(self._pool[start : start + window])


class CipherSuiteAdapter(HTTPAdapter):
    """HTTPAdapter that enforces a custom TLS cipher suite and ECDH curve."""

    __attrs__ = HTTPAdapter.__attrs__ + [
        "ssl_context",
        "cipher_suite",
        "source_address",
        "server_hostname",
        "ecdh_curve",
        "verify_ssl",
    ]

    def __init__(
        self,
        *args,
        cipher_suite: str | None = None,
        ecdh_curve: str = "prime256v1",
        server_hostname: str | None = None,
        source_address: str | tuple | None = None,
        ssl_context: ssl.SSLContext | None = None,
        verify_ssl: bool = True,
        **kwargs,
    ) -> None:
        self.cipher_suite = cipher_suite
        self.ecdh_curve = ecdh_curve
        self.server_hostname = server_hostname
        self.verify_ssl = verify_ssl

        if isinstance(source_address, str):
            source_address = (source_address, 0)
        self.source_address = source_address

        self.ssl_context = ssl_context or self._build_ssl_context()

        super().__init__(*args, **kwargs)

    def _build_ssl_context(self) -> ssl.SSLContext:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        # Stash the original wrap_socket so _wrap_socket can delegate to it.
        context.orig_wrap_socket = context.wrap_socket  # type: ignore[attr-defined]
        context.wrap_socket = self._wrap_socket  # type: ignore[method-assign]

        if self.server_hostname:
            context.server_hostname = self.server_hostname  # type: ignore[attr-defined]
        if self.cipher_suite:
            context.set_ciphers(self.cipher_suite)
        context.set_ecdh_curve(self.ecdh_curve)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3

        if not self.verify_ssl:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        return context

    def _wrap_socket(self, *args, **kwargs) -> Any:
        context = self.ssl_context
        assert context is not None
        if getattr(context, "server_hostname", None):
            kwargs["server_hostname"] = context.server_hostname  # type: ignore[attr-defined]
            context.check_hostname = False
        else:
            context.check_hostname = self.verify_ssl
        return context.orig_wrap_socket(*args, **kwargs)  # type: ignore[attr-defined]

    def init_poolmanager(self, *args, **kwargs) -> None:
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = self.source_address
        super().init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs) -> Any:
        kwargs["ssl_context"] = self.ssl_context
        kwargs["source_address"] = self.source_address
        return super().proxy_manager_for(*args, **kwargs)
