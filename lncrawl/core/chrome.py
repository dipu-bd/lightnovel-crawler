# https://github.com/ultrafunkamsterdam/undetected-chromedriver
# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2

import atexit
import logging
import os
import time
from collections import namedtuple
from threading import Semaphore
from typing import List, Optional

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from .soup import SoupMaker

MAX_CHROME_INSTANCES = 8

logger = logging.getLogger(__name__)

try:
    import selenium.webdriver.support.expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.virtual_authenticator import (
        Transport,
        VirtualAuthenticatorOptions,
    )
    from selenium.webdriver.remote.remote_connection import LOGGER
    from selenium.webdriver.support.wait import WebDriverWait

    LOGGER.setLevel(logging.ERROR)
except ImportError:
    logger.warn("`selenium` is not found")

try:
    import undetected_chromedriver as webdriver
    from undetected_chromedriver import ChromeOptions

    webdriver.logger.setLevel(logging.WARN)
except ImportError:
    logger.warn("`undetected-chromedriver` is not found")

try:
    from webdriver_manager.chrome import ChromeDriverManager

    webdriver_path = ChromeDriverManager().install()
except ImportError:
    logger.warn("`webdriver-manager` is not found")


__all__ = [
    "By",
    "Chrome",
    "Selector",
]


Selector = namedtuple(
    typename="ElementSelector",
    field_names=["by", "value"],
    defaults=[By.ID, None],
)


class Chrome(SoupMaker):
    def __init__(
        self,
        max_instances: int = MAX_CHROME_INSTANCES,
        driver_path: Optional[str] = None,
        options: Optional[ChromeOptions] = None,
        auth_options: Optional[VirtualAuthenticatorOptions] = None,
    ) -> None:
        self.open_browsers: List[webdriver.Chrome] = []

        if not isinstance(max_instances, int):
            max_instances = MAX_CHROME_INSTANCES
        self.semaphore = Semaphore(max_instances)
        logger.debug("Maximum instances: %d", max_instances)

        if not driver_path or not os.path.isfile(str(driver_path)):
            driver_path = webdriver_path
        self.driver_path = str(driver_path)
        logger.debug("Driver path: %s", driver_path)

        self.options = options
        logger.debug("Chrome options: %s", options)

        if not isinstance(auth_options, VirtualAuthenticatorOptions):
            auth_options = VirtualAuthenticatorOptions()
        auth_options = VirtualAuthenticatorOptions()
        auth_options.transport = Transport.INTERNAL
        auth_options.has_user_verification = True
        auth_options.is_user_verified = True
        auth_options.is_user_consenting = True
        self.auth_options = auth_options

        atexit.register(self.cleanup)

    def cleanup(self):
        for chrome in list(self.open_browsers):
            chrome.quit()

    def browser(self, timeout: Optional[float] = None) -> webdriver.Chrome:
        """
        Acquire a chrome browser instane. There is a limit of the number of
        browser instances you can keep open at a time. You must call quit()
        to cleanup existing browser.

        ```
        chrome = Chrome().browser()
        chrome.quit()
        ```

        NOTE: You must call quit() to cleanup the queue.
        """
        if not self.semaphore.acquire(True, timeout):
            raise Exception("Failed to acquire semaphore")

        logger.debug("Created new chrome browser instance")
        chrome = webdriver.Chrome(
            debug=False,
            headless=True,
            options=self.options,
            log_level=logging.ERROR,
            enable_cdp_events=False,
            driver_executable_path=self.driver_path,
        )
        chrome.add_virtual_authenticator(self.auth_options)
        logger.info("Created new instance: %s", chrome.session_id)

        def _decorate(fun):
            def _inner(*args, **kwargs):
                if chrome in self.open_browsers:
                    self.semaphore.release()
                    self.open_browsers.remove(chrome)
                    logger.info("Destroyed instance: %s", chrome.session_id)
                fun(*args, **kwargs)

            return _inner

        chrome.quit = _decorate(chrome.quit)
        self.open_browsers.append(chrome)
        return chrome

    def get_html(
        self,
        url: str,
        timeout: float = 300,
        wait_for: Optional[Selector] = None,
        cookies: Optional[RequestsCookieJar] = None,
    ) -> str:
        chrome = None
        try:
            _start = time.time()
            chrome = self.browser(timeout)

            if isinstance(cookies, RequestsCookieJar):
                for cookie in cookies:
                    chrome.add_cookie(
                        {
                            "name": cookie.name,
                            "value": cookie.value,
                            "path": cookie.path,
                            "domain": cookie.domain,
                            "secure": cookie.secure,
                            "expiry": cookie.expires,
                        }
                    )
                logger.debug("Cookies applied: %s", chrome.get_cookies())

            chrome.get(url)

            if isinstance(cookies, RequestsCookieJar):
                for cookie in chrome.get_cookies():
                    cookies.set(
                        name=cookie.get("name"),
                        value=cookie.get("value"),
                        path=cookie.get("path"),
                        domain=cookie.get("domain"),
                        secure=cookie.get("secure"),
                        expires=cookie.get("expiry"),
                    )
                logger.debug("Cookies retrieved: %s", cookies)

            if wait_for:
                _remains = timeout - (time.time() - _start)
                logger.info(
                    "Waiting maximum of %d seconds for %s to be visible",
                    _remains,
                    wait_for,
                )
                waiter = WebDriverWait(chrome, _remains)
                waiter.until(EC.visibility_of((wait_for.by, wait_for.value)))

            return chrome.page_source
        finally:
            if chrome:
                chrome.quit()

    def get_soup(
        self,
        url,
        timeout: float = 300,
        wait_for: Optional[Selector] = None,
        cookies: Optional[RequestsCookieJar] = None,
    ) -> BeautifulSoup:
        html = self.get_html(
            url=url,
            timeout=timeout,
            wait_for=wait_for,
            cookies=cookies,
        )
        return self.make_soup(html)
