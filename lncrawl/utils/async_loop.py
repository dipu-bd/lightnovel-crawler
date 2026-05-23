import asyncio
from concurrent.futures import Future
import logging
import threading
from typing import Any, Coroutine, Optional, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")

_loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
_thread: threading.Thread = threading.Thread(
    target=_loop.run_forever, daemon=True, name="nodriver-loop"
)
_thread.start()


def run_async(coro: Coroutine[Any, Any, T], timeout: Optional[float] = None) -> T:
    """Submit an async coroutine to the nodriver event loop and block until done."""
    future: Future[T] = asyncio.run_coroutine_threadsafe(coro, _loop)
    return future.result(timeout=timeout)
