from __future__ import annotations

import atexit
from concurrent.futures import Future, ThreadPoolExecutor, as_completed
from threading import Event, Semaphore, Thread
from typing import Callable, Generator, Iterable, List, Optional, Set, TypeVar

from tqdm import tqdm

from ..context import ctx
from ..exceptions import LNException
from ..utils.ratelimit import RateLimiter

T = TypeVar("T")

_resolver = Semaphore(1)


class TaskManager:
    def __init__(
        self,
        workers: Optional[int] = None,
        ratelimit: Optional[float] = None,
        signal=Event(),
    ) -> None:
        """A helper class for task queueing and parallel task execution.
        It is being used as a superclass of the Crawler.

        Args:
        - workers (int, optional): Number of concurrent workers to expect. Default: 5.
        - ratelimit (float, optional): Number of requests per second.
        """
        self.signal = signal
        self._futures: Set[Future] = set()
        self.init_executor(workers, ratelimit)

    @property
    def executor(self) -> ThreadPoolExecutor:
        return self._executor

    @property
    def futures(self) -> List[Future]:
        return list(self._futures)

    @property
    def workers(self):
        return self._executor._max_workers

    def close(self) -> None:
        self.shutdown()

    def shutdown(self, wait=False):
        self.cancel_futures(self._futures)
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
        if not self.signal:
            self.signal = Event()
        if not self._futures:
            self._futures = set()

        self.close()  # cleanup previous initialization

        if ratelimit and ratelimit > 0:
            workers = 1  # use single worker if ratelimit is being applied
            self._limiter = RateLimiter(ratelimit)
        elif hasattr(self, "_limiter"):
            del self._limiter

        self._executor = ThreadPoolExecutor(
            max_workers=workers or 1,
            thread_name_prefix="lncrawl_scraper",
        )

        self._submit = self._executor.submit
        setattr(self._executor, "submit", self.submit_task)

    def submit_task(self, fn: Callable[..., T], *args, **kwargs) -> Future[T]:
        """Submits a callable to be executed with the given arguments.

        Schedules the callable to be executed as fn(*args, **kwargs) and returns
        a Future instance representing the execution of the callable.

        Returns:
            A Future representing the given call.
        """
        if not self._submit:
            raise Exception("No executor is available")

        if hasattr(self, "_limiter"):
            fn = self._limiter.wrap(fn)

        f = self._submit(fn, *args, **kwargs)
        self._futures.add(f)
        f.add_done_callback(self._futures.remove)

        return f

    @staticmethod
    def progress_bar(
        iterable: Optional[Iterable[T]] = None,
        unit: Optional[str] = None,
        desc: Optional[str] = None,
        total: Optional[float] = None,
        disable: bool = False,
    ) -> tqdm:
        if ctx.logger.is_info:
            disable = True

        if not disable:
            # Since we are showing progress bar, it is not good to
            # resolve multiple list of futures at once
            if not _resolver.acquire(True, 30):
                pass

        bar = tqdm(
            iterable=iterable,
            desc=desc or "",
            unit=unit or "item",
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

    def cancel_futures(self, futures: Iterable[Future[T]]) -> None:
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
        futures: Iterable[Future[T]],
        disable_bar: bool = False,
        desc: Optional[str] = None,
        unit: Optional[str] = None,
        fail_fast: bool = False,
        signal: Optional[Event] = None,
        timeout: Optional[float] = None,
    ) -> Generator[Optional[T], None, None]:
        """Create a generator output to resolve the futures.

        Args:
            futures: A iterable list of futures to resolve.
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
            fail_fast: Fail on first error
            signal: The abort signal
        """
        futures = list(futures)
        if not futures:
            return

        if not signal:
            signal = self.signal
        assert signal

        bar = self.progress_bar(
            total=len(futures),
            desc=desc,
            unit=unit,
            disable=disable_bar,
        )
        try:
            for future in as_completed(futures, timeout):
                if signal.is_set():
                    return  # canceled
                if fail_fast:
                    yield future.result(timeout)
                    bar.update()
                    continue
                try:
                    yield future.result(timeout)
                except KeyboardInterrupt:
                    signal.set()
                    raise
                except LNException as e:
                    bar.clear()
                    print(str(e))
                except Exception as e:
                    yield None
                    if bar.disable:
                        ctx.logger.info(f"Failure to resolve future. {repr(e)}")
                finally:
                    bar.update()
        except KeyboardInterrupt:
            signal.set()
            raise
        finally:
            Thread(
                target=self.cancel_futures,
                kwargs=dict(futures=futures),
                # daemon=True,
            ).start()
            bar.close()

    def resolve_futures(
        self,
        futures: Iterable[Future[T]],
        disable_bar: bool = False,
        desc: Optional[str] = None,
        unit: Optional[str] = None,
        fail_fast: bool = False,
        signal: Optional[Event] = None,
        timeout: Optional[float] = None,
    ):
        """Wait for the futures to be done.

        Args:
            futures: A iterable list of futures to resolve.
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
            fail_fast: Fail on first error
            signal: The abort signal
        """

        return list(
            self.resolve_as_generator(
                futures=futures,
                disable_bar=disable_bar,
                desc=desc,
                unit=unit,
                fail_fast=fail_fast,
                signal=signal,
                timeout=timeout,
            )
        )

    def as_completed(
        self,
        disable_bar: bool = False,
        desc: Optional[str] = None,
        unit: Optional[str] = None,
        fail_fast: bool = False,
        signal: Optional[Event] = None,
        timeout: Optional[float] = None,
    ):
        """Wait for the futures in this task manager to be done.

        Args:
            disable_bar: Hides the progress bar if True.
            desc: The progress bar description
            unit: The progress unit name
            fail_fast: Fail on first error
            signal: The abort signal
        """
        return list(
            self.resolve_as_generator(
                futures=self._futures,
                disable_bar=disable_bar,
                desc=desc,
                unit=unit,
                fail_fast=fail_fast,
                signal=signal,
                timeout=timeout,
            )
        )
