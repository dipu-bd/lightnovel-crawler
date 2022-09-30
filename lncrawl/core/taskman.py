import logging
import os
import signal
import threading
from abc import ABC
from concurrent.futures import Future, ThreadPoolExecutor
from typing import List

from tqdm import tqdm

from .exeptions import LNException

logger = logging.getLogger(__name__)

MAX_WORKER_COUNT = 10


class TaskManager(ABC):
    def __init__(self) -> None:
        self._destroyed = False
        self.init_executor()

    def destroy(self) -> None:
        self._destroyed = True
        self.executor.shutdown(False)

    def init_executor(self, workers: int = MAX_WORKER_COUNT, wait: bool = False):
        if hasattr(self, "executor"):
            if self.executor._max_workers == workers:
                return
            self.executor.shutdown(wait)
        self.executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="lncrawl_scraper",
            initargs=(self),
        )

    def cancel_all(self, futures: List[Future]):
        for future in futures:
            if not future.done():
                future.cancel()

    def resolve_all(self, futures: List[Future], desc="", unit="") -> None:
        if not futures:
            return

        is_debug_mode = os.getenv("debug_mode") == "yes"
        bar = tqdm(
            desc=desc,
            unit=unit,
            total=len(futures),
            disable=is_debug_mode,
        )

        def _cancel(*args):
            bar.close()
            self.cancel_all(futures)
            if len(args):
                raise LNException("Cancelled by user")

        if threading.current_thread() is threading.main_thread():
            signal.signal(signal.SIGINT, _cancel)

        try:
            for future in futures:
                try:
                    message = future.result()
                    if message and not is_debug_mode:
                        bar.clear()
                        logger.warning(message)
                finally:
                    bar.update()
        finally:
            _cancel()
