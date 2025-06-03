from threading import Event


class Aborter:
    def __init__(self) -> None:
        self._event = Event()

    @property
    def aborted(self):
        return self._event.is_set()

    def abort(self):
        self._event.set()

    def wait(self, timeout: float):
        if timeout <= 0:
            return
        self._event.wait(timeout)
