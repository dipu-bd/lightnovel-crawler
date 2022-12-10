import logging
import os
from abc import ABC
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Semaphore, Thread
from typing import Dict, Iterable, List, TypeVar

from tqdm import tqdm

logger = logging.getLogger(__name__)

T = TypeVar("T")

MAX_WORKER_COUNT = 5
MAX_REQUESTS_PER_DOMAIN = 25

_resolver = Semaphore(1)
_host_semaphores: Dict[str, Semaphore] = {}


class TaskManager(ABC):
    def __init__(self, workers: int = MAX_WORKER_COUNT) -> None:
        """A helper class for task queueing and parallel task execution.
        It is being used as a superclass of the Crawler.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 10.
        """
        self._futures: List[Future] = []
        self.init_executor(workers)

    def __del__(self) -> None:
        if hasattr(self, "_executor"):
            self._submit = None
            self._futures.clear()
            self._executor.shutdown(wait=False)

    @property
    def executor(self) -> ThreadPoolExecutor:
        return self._executor

    @property
    def futures(self) -> List[Future]:
        return self._futures

    @property
    def workers(self):
        return self._executor._max_workers

    def init_executor(self, workers: int):
        """Initializes a new executor.

        If the number of workers are not the same as the current executor,
        it will shutdown the current executor, and cancel all pending tasks.

        Args:
        - workers (int): Number of workers to expect in the new executor.
        """
        if hasattr(self, "_executor"):
            if self.workers == workers:
                return
            self._submit = None
            self._futures.clear()
            self._executor.shutdown(wait=False)

        self._executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="lncrawl_scraper",
        )

        self._submit = self._executor.submit
        self._executor.submit = self.submit_task

    def submit_task(self, fn, *args, **kwargs) -> Future:
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        future = self._submit(fn, *args, **kwargs)
        self._futures.append(future)
        return future

    def progress_bar(
        self,
        iterable=None,
        desc=None,
        total=None,
        unit=None,
        disable=False,
        timeout: float = None,
    ):
        if os.getenv("debug_mode"):
            disable = True

        if not disable:
            # Since we are showing progress bar, it is not good to
            # resolve multiple list of futures at once
            if not _resolver.acquire(True, timeout):
                pass

        bar = tqdm(
            iterable=iterable,
            desc=desc,
            unit=unit,
            total=total,
            disable=disable or os.getenv("debug_mode"),
        )

        original_close = bar.close

        def extended_close():
            if not bar.disable:
                _resolver.release()
            original_close()

        bar.close = extended_close

        return bar

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
        desc=None,
        unit=None,
        fail_fast=False,
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

        bar = self.progress_bar(
            desc=desc,
            unit=unit,
            total=len(futures),
            disable=disable_bar,
            timeout=timeout,
        )

        try:
            for future in futures:
                if fail_fast:
                    future.result(timeout)
                    bar.update()
                    continue
                try:
                    future.result(timeout)
                except Exception as e:
                    if isinstance(e, KeyboardInterrupt):
                        break
                    if bar.disable:
                        logger.exception("Failure to resolve future")
                    else:
                        bar.clear()
                        logger.warning(f"{type(e).__name__}: {e}")
                finally:
                    bar.update()
        finally:
            Thread(target=lambda: self.cancel_futures(futures)).start()
            bar.close()
