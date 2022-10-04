# https://github.com/ultrafunkamsterdam/undetected-chromedriver
# https://cloudbytes.dev/snippets/run-selenium-and-chrome-on-wsl2

import atexit
import logging
from threading import Lock, Semaphore
from typing import Iterable, List, Optional

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from .. import chromedriver as webdriver
from ..chromedriver import ChromeOptions
from ..utils.platforms import Platform, Screen
from .soup import SoupMaker

logger = logging.getLogger(__name__)

try:
    import selenium.webdriver.common.virtual_authenticator as VAuth
    import selenium.webdriver.support.expected_conditions as EC
    from selenium.webdriver.common.by import By
    from selenium.webdriver.remote.remote_connection import LOGGER
    from selenium.webdriver.support.wait import WebDriverWait

    # from selenium.webdriver.remote.command import Command
    # from selenium.webdriver.remote.webelement import WebElement

    LOGGER.setLevel(logging.ERROR)
except ImportError:
    logger.warn("`selenium` is not found")

try:
    from webdriver_manager.chrome import ChromeDriverManager
except ImportError:
    logger.warn("`webdriver-manager` is not found")


__all__ = [
    "By",
    "EC",
    "Browser",
    "create_chrome",
]


MAX_BROWSER_INSTANCES = 8

__installer_lock = Lock()
__semaphore = Semaphore(MAX_BROWSER_INSTANCES)
__open_browsers: List[webdriver.Chrome] = []


def __get_driver_path():
    with __installer_lock:
        return ChromeDriverManager().install()


def __decorate(chrome, method_name):
    fun = getattr(chrome, method_name)

    def _inner(*args, **kwargs):
        if chrome in __open_browsers:
            __semaphore.release()
            __open_browsers.remove(chrome)
            logger.info("Destroyed instance: %s", chrome.session_id)
        fun(*args, **kwargs)

    setattr(chrome, method_name, _inner)


def create_chrome(
    options: Optional[ChromeOptions] = None,
    timeout: Optional[float] = None,
    headless: bool = True,
) -> webdriver.Chrome:
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
    assert __semaphore.acquire(True, timeout), "Failed to acquire semaphore"

    if not isinstance(options, ChromeOptions):
        options = ChromeOptions()

    if not Platform.display:
        headless = True

    if not headless:
        width = int(max(640, Screen.view_width * 2 / 3))
        height = int(max(480, Screen.view_height * 2 / 3))
        options.add_argument(f"--window-size={width},{height}")

    driver_path = __get_driver_path()

    logger.debug(
        f"Creating chrome instance | headerless={headless} | options={options} | path={driver_path}"
    )
    chrome = webdriver.Chrome(
        debug=False,
        options=options,
        headless=headless,
        log_level=logging.ERROR,
        enable_cdp_events=False,
        driver_executable_path=driver_path,
    )
    chrome.set_window_position(0, 0)
    __open_browsers.append(chrome)
    __decorate(chrome, "quit")

    auth_options = VAuth.VirtualAuthenticatorOptions()
    auth_options.transport = VAuth.Transport.INTERNAL
    auth_options.has_user_verification = True
    auth_options.is_user_verified = True
    auth_options.is_user_consenting = True
    chrome.add_virtual_authenticator(auth_options)

    logger.info(f"Created new chrome. session_id={chrome.session_id}")
    return chrome


def cleanup():
    for chrome in __open_browsers:
        chrome.quit()


atexit.register(cleanup)


class Browser:
    def __init__(
        self,
        headless: bool = True,
        timeout: Optional[int] = 300,
        options: Optional[ChromeOptions] = None,
        cookie_store: Optional[RequestsCookieJar] = None,
        soup_parser: Optional[str] = None,
    ) -> None:
        self._driver = None
        self.options = options
        self.timeout = timeout
        self.headless = headless
        self.cookie_store = cookie_store
        self._soup_tool = SoupMaker(soup_parser)

    def __del__(self):
        if not isinstance(self._driver, webdriver.Chrome):
            return
        self._restore_cookies()
        self._driver.quit()

    def __enter__(self):
        self._init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not isinstance(self._driver, webdriver.Chrome):
            return
        self._restore_cookies()
        self._driver.quit()

    def _init_browser(self):
        if isinstance(self._driver, webdriver.Chrome):
            return
        self._driver = create_chrome(
            options=self.options,
            timeout=self.timeout,
            headless=self.headless,
        )
        self._apply_cookies()

    def _apply_cookies(self):
        if not isinstance(self._driver, webdriver.Chrome):
            return
        if not isinstance(self.cookie_store, RequestsCookieJar):
            return
        for cookie in self.cookie_store:
            self._driver.add_cookie(
                {
                    "name": cookie.name,
                    "value": cookie.value,
                    "path": cookie.path,
                    "domain": cookie.domain,
                    "secure": cookie.secure,
                    "expiry": cookie.expires,
                }
            )
        logger.debug("Cookies applied: %s", self._driver.get_cookies())

    def _restore_cookies(self):
        if not isinstance(self._driver, webdriver.Chrome):
            return
        if not isinstance(self.cookie_store, RequestsCookieJar):
            return
        for cookie in self._driver.get_cookies():
            self.cookie_store.set(
                name=cookie.get("name"),
                value=cookie.get("value"),
                path=cookie.get("path"),
                domain=cookie.get("domain"),
                secure=cookie.get("secure"),
                expires=cookie.get("expiry"),
            )
        logger.debug("Cookies retrieved: %s", self.cookie_store)

    @property
    def current_url(self):
        """Get the current url if available, otherwise None"""
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        return self._driver.current_url

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session id if available, otherwise None"""
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        return self._driver.session_id

    @property
    def html(self) -> str:
        """Get the current page html"""
        if not isinstance(self._driver, webdriver.Chrome):
            return ""
        return str(self._driver.page_source)

    @property
    def soup(self) -> BeautifulSoup:
        """Get the current page soup"""
        # Return from cache if available
        old_html = getattr(self, "_html_", None)
        if old_html == self.html:
            return getattr(self, "_soup")
        # Create new soup and save to cache
        soup = self._soup_tool.make_soup(self.html)
        setattr(self, "_html_", self.html)
        setattr(self, "_soup_", soup)
        return soup

    def visit(self, url: str) -> None:
        """Visit an URL. Create new session if it does not exist"""
        self._init_browser()
        self._driver.get(url)

    # def find(self, selector: str, by=By.CSS_SELECTOR) -> WebElement:
    #     if not isinstance(self._driver, webdriver.Chrome):
    #         return None
    #     self._driver.find_element(by, selector)

    # def find_all(self, selector: str, by=By.CSS_SELECTOR) -> List[WebElement]:
    #     if not isinstance(self._driver, webdriver.Chrome):
    #         return None
    #     self._driver.find_elements(by, selector)

    def click(self, selector: str, by=By.CSS_SELECTOR) -> None:
        "Select and click on an element."
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        self._driver.find_element(by, selector).click()

    def submit(self, selector: str, by=By.CSS_SELECTOR) -> None:
        """Select a form and submit it."""
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        self._driver.find_element(by, selector).submit()

    def send_keys(
        self, selector: str, by=By.CSS_SELECTOR, value: str = "", clear: bool = True
    ) -> None:
        """Select a form and submit it."""
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        elem = self._driver.find_element(by, selector)
        if clear:
            elem.clear()
        elem.send_keys(value)

    def execute_js(self, script: str, *args, is_async=False):
        """
        Executes JavaScript in the current browser window.

        :Args:
         - script: The JavaScript to execute.
         - \\*args: Any applicable arguments for your JavaScript.
         - is_async: Whether to run as async script
        """
        if not isinstance(self._driver, webdriver.Chrome):
            return None
        if is_async:
            self._driver.execute_async_script(script, *args)
        else:
            self._driver.execute_script(script, *args)

    def wait(
        self,
        selector: str,
        by: str = By.CSS_SELECTOR,
        timeout: Optional[float] = 60,
        poll_frequency: Optional[float] = 0.5,
        ignored_exceptions: Iterable[Exception] = [],
        expected_conditon=EC.visibility_of_all_elements_located,
    ):
        """Waits for a element to be visible on the current page by CSS selector.

        :Args:
         - chrome - Instance of WebDriver / Browser
         - timeout - Number of seconds before timing out
         - poll_frequency - Sleep interval between calls. Default: 0.5
         - ignored_exceptions - List of exception classes to ignore. Default: [NoSuchElementException]
        """
        if not isinstance(self._driver, webdriver.Chrome):
            return
        if not selector or not callable(expected_conditon):
            return
        logger.info(
            f"Wait {timeout} seconds for {expected_conditon.__name__} by {by}:{selector}"
        )
        try:
            waiter = WebDriverWait(
                self._driver, timeout, poll_frequency, ignored_exceptions
            )
            waiter.until(expected_conditon((by, selector)))
        except Exception as e:
            logger.info("Waiting could not be finished | %s", e)
