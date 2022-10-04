import logging
from typing import Iterable, Optional

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar

from ..chromedriver.chrome import (
    EC,
    By,
    ChromeOptions,
    WebDriver,
    WebDriverWait,
    create_chrome,
)
from .soup import SoupMaker

logger = logging.getLogger(__name__)


__all__ = [
    "By",
    "EC",
    "Browser",
    "create_chrome",
]


class Browser:
    def __init__(
        self,
        headless: bool = True,
        timeout: Optional[int] = 300,
        options: Optional["ChromeOptions"] = None,
        cookie_store: Optional[RequestsCookieJar] = None,
        soup_parser: Optional[str] = None,
    ) -> None:
        self._driver: WebDriver = None
        self.options = options
        self.timeout = timeout
        self.headless = headless
        self.cookie_store = cookie_store
        self._soup_tool = SoupMaker(soup_parser)

    def __del__(self):
        if not self._driver:
            return
        self._restore_cookies()
        self._driver.quit()

    def __enter__(self):
        self._init_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._driver:
            return
        self._restore_cookies()
        self._driver.quit()

    def _init_browser(self):
        if self._driver:
            return
        self._driver = create_chrome(
            options=self.options,
            timeout=self.timeout,
            headless=self.headless,
        )
        self._apply_cookies()

    def _apply_cookies(self):
        if not self._driver:
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
        if not self._driver:
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
        if not self._driver:
            return None
        return self._driver.current_url

    @property
    def session_id(self) -> Optional[str]:
        """Get the current session id if available, otherwise None"""
        if not self._driver:
            return None
        return self._driver.session_id

    @property
    def html(self) -> str:
        """Get the current page html"""
        if not self._driver:
            return ""
        return str(self._driver.page_source)

    @property
    def soup(self) -> BeautifulSoup:
        """Get the current page soup"""
        # Return from cache if available
        old_html = getattr(self, "_html_", None)
        if old_html == self.html:
            return getattr(self, "_soup_")
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
    #     if not self._driver:
    #         return None
    #     self._driver.find_element(by, selector)

    # def find_all(self, selector: str, by=By.CSS_SELECTOR) -> List[WebElement]:
    #     if not self._driver:
    #         return None
    #     self._driver.find_elements(by, selector)

    def click(self, selector: str, by=By.CSS_SELECTOR) -> None:
        "Select and click on an element."
        if not self._driver:
            return None
        self._driver.find_element(by, selector).click()

    def submit(self, selector: str, by=By.CSS_SELECTOR) -> None:
        """Select a form and submit it."""
        if not self._driver:
            return None
        self._driver.find_element(by, selector).submit()

    def send_keys(
        self, selector: str, by=By.CSS_SELECTOR, value: str = "", clear: bool = True
    ) -> None:
        """Select a form and submit it."""
        if not self._driver:
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
        if not self._driver:
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
        if not self._driver:
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