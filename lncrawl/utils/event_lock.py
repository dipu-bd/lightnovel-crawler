from threading import Event, Semaphore
from typing import Optional

from ..exceptions import AbortedException


class EventLock:
    def __init__(self, concurrency=1) -> None:
        self._default_signal = Event()
        self._sema = Semaphore(concurrency)
        self._signal = self._default_signal

    def abort(self):
        self._default_signal.set()

    def using(self, signal: Optional[Event] = None):
        if signal:
            self._signal = signal
        return self

    def acquire(self):
        while not self._signal.is_set():
            if self._sema.acquire(timeout=0.1):
                return True
        return False

    def release(self):
        self._sema.release()

    def __enter__(self):
        if not self.acquire():
            raise AbortedException()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._signal = self._default_signal  # reset
        self.release()
        return False
