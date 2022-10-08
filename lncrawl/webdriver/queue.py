import atexit
import logging
from threading import Semaphore, Thread
from typing import List, Optional

from selenium.webdriver.remote.webdriver import WebDriver

logger = logging.getLogger(__name__)

MAX_BROWSER_INSTANCES = 8

__open_browsers: List[WebDriver] = []
__semaphore = Semaphore(MAX_BROWSER_INSTANCES)


def __override_quit(driver: WebDriver):
    __open_browsers.append(driver)
    original = Thread(target=driver.quit)

    def override():
        if driver in __open_browsers:
            __semaphore.release()
            __open_browsers.remove(driver)
            logger.info("Destroyed instance: %s", driver.session_id)
        if not original._started.is_set():
            original.start()

    driver.quit = override


def _acquire_queue(timeout: Optional[float] = None):
    acquired = __semaphore.acquire(True, timeout)
    if not acquired:
        raise TimeoutError("Failed to acquire semaphore")


def _release_queue(driver: WebDriver):
    __override_quit(driver)


def check_active(driver: WebDriver) -> bool:
    if not isinstance(driver, WebDriver):
        return False
    return driver in __open_browsers


def cleanup_drivers():
    for driver in __open_browsers:
        driver.close()
        driver.quit()


atexit.register(cleanup_drivers)
