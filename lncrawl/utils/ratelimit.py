import logging
import time

logger = logging.getLogger(__name__)


class RateLimiter(object):
    """A helper class for a controlling number of requests per seconds.
    It is being used along with the TaskManager class.

    Args:
    - ratelimit (float, optional): Number of requests per seconds.
    """

    def __init__(self, ratelimit: float):
        if ratelimit <= 0:
            raise ValueError("ratelimit should be a non-zero positive number")
        self.period = 1 / ratelimit
        self._closed = False

    def _now(self):
        if hasattr(time, "monotonic"):
            return time.monotonic()
        return time.time()

    def __enter__(self):
        self._time = self._now()

    def __exit__(self, type, value, traceback):
        if self._closed:
            return
        d = (self._time + self.period) - self._now()
        self._time = self._now()
        if d > 0:
            time.sleep(d)

    def shutdown(self):
        self._closed = True

    def wrap(self, fn):
        def inner(*args, **kwargs):
            with self:
                return fn(*args, **kwargs)

        return inner
