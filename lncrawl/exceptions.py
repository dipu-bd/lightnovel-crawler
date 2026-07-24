from typing import TYPE_CHECKING, Any
from urllib.error import URLError

from PIL import UnidentifiedImageError
from requests.exceptions import RequestException
from scraper.exceptions import AbortedException, CloudflareException
from urllib3.exceptions import HTTPError

if TYPE_CHECKING:
    # Server-only, FastAPI-dependent names. Kept out of the runtime import graph
    # so the CLI crawl path never pulls in FastAPI; resolved lazily via
    # ``__getattr__`` and statically via this block (see _server_errors).
    from ._server_errors import (
        ServerError,
        ServerErrors,
        WebSocketError,
        WebSocketErros,
        get_exception_handlers,
    )

__all__ = [
    "LNException",
    "ServerError",
    "ServerErrors",
    "WebSocketError",
    "WebSocketErros",
    "AbortedException",
    "RetryErrorGroup",
    "ScraperErrorGroup",
    "FallbackToBrowser",
    "get_exception_handlers",
]


class LNException(Exception):
    pass


class FallbackToBrowser(Exception):
    pass


ScraperErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    FallbackToBrowser,
    UnidentifiedImageError,
)

RetryErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    UnidentifiedImageError,
)

# Names served lazily from the FastAPI-dependent submodule.
_SERVER_NAMES = frozenset(
    {
        "ServerError",
        "ServerErrors",
        "WebSocketError",
        "WebSocketErros",
        "get_exception_handlers",
    }
)


def __getattr__(name: str) -> Any:
    if name in _SERVER_NAMES:
        from . import _server_errors

        return getattr(_server_errors, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
