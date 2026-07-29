from typing import TYPE_CHECKING, Any
from urllib.error import URLError

from PIL import UnidentifiedImageError
from requests.exceptions import RequestException

# `AbortedException` is lncrawl's own exported name and stays as it is: the scraper
# renamed the class to `Aborted` in 1.0, and chasing that through ~45 raise/except
# sites would churn every job handler for no behavioural change.
from scraper.exceptions import Aborted as AbortedException, Blocked, Poisoned
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


# `Blocked` is the scraper's base for an attributed retrieval failure, so it covers
# `Impassable` and `Exhausted` too. `Poisoned` means the page came back but is believed
# to be decoy filler — a failure a caller must not treat as content.
ScraperErrorGroup = (
    URLError,
    HTTPError,
    Blocked,
    Poisoned,
    RequestException,
    FallbackToBrowser,
    UnidentifiedImageError,
)

# Deliberately without `Poisoned`: the scraper raises it for a URL it has already
# recorded as decoy, so asking again returns the same filler. Retrying is the one
# response guaranteed not to help.
RetryErrorGroup = (
    URLError,
    HTTPError,
    Blocked,
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
