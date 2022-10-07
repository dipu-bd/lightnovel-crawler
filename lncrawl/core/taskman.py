import logging
import os
from abc import ABC
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Semaphore
from typing import Dict, Iterable, TypeVar

from tqdm import tqdm

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_WORKER_COUNT = 10
MAX_REQUESTS_PER_DOMAIN = 25

_resolver = Semaphore(1)
_host_semaphores: Dict[str, Semaphore] = {}


class TaskManager(ABC):
    def __init__(self, workers: int = MAX_WORKER_COUNT) -> None:
        self.init_executor(workers)

    @property
    def executor(self):
        return self._executor

    def __del__(self) -> None:
        self._executor.shutdown(wait=False)

    def init_executor(self, workers: int):
        """Initializes a new executor.

        If the number of workers are not the same as the current executor,
        it will shutdown the current executor, and cancel all pending tasks.

        Args:
            workers: Number of workers to expect in the new executor.
        """
        if hasattr(self, "_executor"):
            if self._executor._max_workers == workers:
                return
            self._executor.shutdown(wait=False)
        self._executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="lncrawl_scraper",
            initargs=(self),
        )

    def cancel_futures(self, futures: Iterable[Future]) -> None:
        """Cancels all the future that are not yet done.

        Args:
            futures: A iterable list of futures to cancel.
        """
        if not futures:
            return
        for future in futures:
            if not future.done():
                future.cancel()

    def resolve_futures(
        self,
        futures: Iterable[Future],
        timeout: float = None,
        disable_bar=False,
        desc: str = "",
        unit: str = "",
    ) -> None:
        """Wait for the futures to be done.

        Args:
            futures: A iterable list of futures to resolve.
            timeout: The number of seconds to wait for the result of a future.
                If None, then there is no limit on the wait time.
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
        """
        if not futures:
            return

        if os.getenv("debug_mode"):
            disable_bar = True

        if not disable_bar:
            # Since we are showing progress bar, it is not good to
            # resolve multiple list of futures at once
            if not _resolver.acquire(True, timeout):
                pass

        try:
            bar = tqdm(
                desc=desc,
                unit=unit,
                total=len(futures),
                disable=disable_bar,
            )
            for future in futures:
                try:
                    future.result(timeout)
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        break
                    message = f"{type(e).__name__}: {e}"
                    if not disable_bar:
                        bar.clear()
                    logger.warning(message)
                finally:
                    bar.update()
        finally:
            bar.close()
            if not disable_bar:
                _resolver.release()
            self.cancel_futures(futures)

    def domain_gate(self, hostname: str = ""):
        """Limit number of entry per hostname.

        Args:
            url: A fully qualified url.

        Returns:
            A semaphore object to wait.

        Example:
            with self.domain_gate(url):
                self.scraper.get(url)
        """
        if hostname not in _host_semaphores:
            _host_semaphores[hostname] = Semaphore(MAX_REQUESTS_PER_DOMAIN)
        return _host_semaphores[hostname]
