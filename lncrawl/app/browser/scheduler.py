# -*- coding: utf-8 -*-

import logging
import time
from threading import BoundedSemaphore, Lock
from urllib.parse import urlparse

from ..config import CONFIG

logger = logging.getLogger(__name__)

mutex = Lock()
host_configs = dict()
host_semaphores = dict()
semaphore = BoundedSemaphore(CONFIG.get('concurrency/max_connections'))


class ConnectionControl:
    '''Controls concurrent connections per instance

    If 'timeout' is None (the default), the default timeout is used.
    If 'timeout' is a non-negative number, blocks at most 'timeout' seconds.
    After which it raises a TimeoutError exception if no slot is available.
    '''

    def __init__(self, url: str, timeout: float = None):
        self.timeout = timeout
        self.hostname = urlparse(url).netloc
        self.max_connections = CONFIG.get('concurrency/per_host/max_connections')
        if timeout is None or timeout < 0:
            self.timeout = CONFIG.get('concurrency/per_host/semaphore_timeout')

    def __enter__(self):
        start_time = time.time()

        # Get a global semaphore lock or raise TimeoutError
        endtime = self.timeout - (time.time() - start_time)
        if not semaphore.acquire(True, endtime):
            raise TimeoutError('Global semaphore acquire failed')

        # Create hostname semaphore if not exists
        endtime = self.timeout - (time.time() - start_time)
        if self.hostname not in host_semaphores:
            if not mutex.acquire(True, endtime):
                semaphore.release()
                raise TimeoutError('Mutex lock acquire failed')
            if self.hostname not in host_semaphores:
                host_semaphores[self.hostname] = BoundedSemaphore(self.max_connections)
            mutex.release()

        self.host_semaphore: Semaphore = host_semaphores[self.hostname]

        # Get a host specific semaphore lock or raise TimeoutError
        endtime = self.timeout - (time.time() - start_time)
        if not self.host_semaphore.acquire(True, endtime):
            semaphore.release()
            raise TimeoutError('Host semaphore acquire failed')

        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.host_semaphore.release()
        semaphore.release()
