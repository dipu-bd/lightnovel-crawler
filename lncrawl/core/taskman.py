import atexit
import logging
import os
from abc import ABC
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Semaphore, Thread
from typing import Any, Dict, Generator, Iterable, List, Optional

from tqdm import tqdm

from .exeptions import LNException
from ..utils.ratelimit import RateLimiter

logger = logging.getLogger(__name__)

MAX_REQUESTS_PER_DOMAIN = 5

_resolver = Semaphore(1)
_host_semaphores: Dict[str, Semaphore] = {}


class TaskManager(ABC):
    def __init__(
        self,
        workers: Optional[int] = None,
        ratelimit: Optional[float] = None,
    ) -> None:
        """A helper class for task queueing and parallel task execution.
        It is being used as a superclass of the Crawler.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 5.
        - ratelimit (float, optional): Number of requests per second.
        """
        self.init_executor(workers, ratelimit)

    def __del__(self) -> None:
        self.shutdown()

    @property
    def executor(self) -> ThreadPoolExecutor:
        return self._executor

    @property
    def futures(self) -> List[Future]:
        return self._futures

    @property
    def workers(self):
        return self._executor._max_workers

    def shutdown(self, wait=False):
        if hasattr(self, "_executor"):
            self._submit = None
            self._executor.shutdown(wait)
        if hasattr(self, "_limiter"):
            self._limiter.shutdown()

    def init_executor(
        self,
        workers: Optional[int] = None,
        ratelimit: Optional[float] = None,
    ):
        """Initializes a new executor.

        If the number of workers are not the same as the current executor,
        it will shutdown the current executor, and cancel all pending tasks.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 5.
        - ratelimit (float, optional): Number of requests per second.
        """
        self._futures: List[Future] = []
        self.__del__()  # cleanup previous initialization

        if ratelimit and ratelimit > 0:
            workers = 1  # use single worker if ratelimit is being applied
            self._limiter = RateLimiter(ratelimit)
        elif hasattr(self, "_limiter"):
            del self._limiter

        self._executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="lncrawl_scraper",
        )

        self._submit = self._executor.submit
        setattr(self._executor, "submit", self.submit_task)

    def submit_task(self, fn, *args, **kwargs) -> Future:
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        if hasattr(self, "_limiter"):
            fn = self._limiter.wrap(fn)
        if not self._submit:
            raise Exception("No executor is available")
        future = self._submit(fn, *args, **kwargs)
        self._futures.append(future)
        return future

    @staticmethod
    def progress_bar(
        iterable: Optional[Iterable] = None,
        unit: Optional[str] = None,
        desc: Optional[str] = None,
        total: Optional[float] = None,
        timeout: Optional[float] = None,
        disable: bool = False,
    ) -> tqdm:
        if os.getenv("debug_mode"):
            disable = True

        if not disable:
            # Since we are showing progress bar, it is not good to
            # resolve multiple list of futures at once
            if not _resolver.acquire(True, timeout):
                pass

        bar = tqdm(
            iterable=iterable,
            desc=desc or '',
            unit=unit or 'item',
            total=total,
            disable=disable,
        )

        original_close = bar.close
        atexit.register(original_close)

        def extended_close() -> None:
            atexit.unregister(original_close)
            if not bar.disable:
                _resolver.release()
            original_close()

        bar.close = extended_close  # type: ignore
        return bar

    def domain_gate(self, hostname: Optional[str]):
        """Limit number of entry per hostname.

        Args:
            hostname: A fully qualified url.

        Returns:
            A semaphore object to wait.

        Example:
            with self.domain_gate(url):
                self.scraper.get(url)
        """
        if hostname is None:
            hostname = ''
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

    def resolve_as_generator(
        self,
        futures: Iterable[Future],
        timeout: Optional[float] = None,
        disable_bar: bool = False,
        desc: Optional[str] = None,
        unit: Optional[str] = None,
        fail_fast: bool = False,
    ) -> Generator[Any, None, None]:
        """Create a generator output to resolve the futures.

        Args:
            futures: A iterable list of futures to resolve.
            timeout: The number of seconds to wait for the result of a future.
                If None, then there is no limit on the wait time.
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
            fail_fast: Fail on first error
        """
        bar = self.progress_bar(
            futures,
            desc=desc,
            unit=unit,
            timeout=timeout,
            disable=disable_bar,
        )
        try:
            for step in bar:
                future: Future = step
                if fail_fast:
                    yield future.result(timeout)
                    bar.update()
                    continue
                try:
                    yield future.result(timeout)
                except KeyboardInterrupt:
                    raise
                except LNException as e:
                    bar.clear()
                    print(str(e))
                except Exception as e:
                    yield None
                    if bar.disable:
                        logger.exception("Failure to resolve future")
                    else:
                        bar.clear()
                        logger.warning(f"{type(e).__name__}: {e}")
                finally:
                    bar.update()
        except KeyboardInterrupt:
            raise
        finally:
            Thread(target=lambda: self.cancel_futures(futures)).start()
            yield from ()
            bar.close()

    def resolve_futures(
        self,
        futures: Iterable[Future],
        timeout: Optional[float] = None,
        disable_bar: bool = False,
        desc: Optional[str] = None,
        unit: Optional[str] = None,
        fail_fast: bool = False,
    ) -> list:
        """Wait for the futures to be done.

        Args:
            futures: A iterable list of futures to resolve.
            timeout: The number of seconds to wait for the result of a future.
                If None, then there is no limit on the wait time.
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
            fail_fast: Fail on first error
        """

        return list(
            self.resolve_as_generator(
                futures=futures,
                timeout=timeout,
                disable_bar=disable_bar,
                desc=desc,
                unit=unit,
                fail_fast=fail_fast,
            )
        )
