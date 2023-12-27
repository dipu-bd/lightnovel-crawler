import logging
from typing import Any, Iterable, List, Optional

from bs4 import BeautifulSoup
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from ..webdriver import ChromeOptions, WebDriver, create_new
from ..webdriver.elements import EC, By, WebElement
from ..webdriver.job_queue import check_active
from .soup import SoupMaker

logger = logging.getLogger(__name__)


class Browser:
    def __init__(
        self,
        headless: bool = True,
        timeout: Optional[int] = 120,
        options: Optional["ChromeOptions"] = None,
        cookie_store: Optional[RequestsCookieJar] = None,
        browser_storage: Optional[dict] = None,
        soup_maker: Optional[SoupMaker] = None,
    ) -> None:
        """
        Interface to interact with chrome webdriver.

        Args:
        - headless (bool, optional): True to hide the UI, False to show the UI. Default: True.
        - timeout (Optional[int], optional): Maximum wait duration in seconds for an element to be available. Default: 120.
        - options (Optional[&quot;ChromeOptions&quot;], optional): Webdriver options. Default: None.
        - cookie_store (Optional[RequestsCookieJar], optional): A cookie store to synchronize cookies. Default: None.
        - browser_storage (Optional[dict], optional): A Storage to save some user info that is saved in your Browser storage. Default: None.
        - soup_parser (Optional[str], optional): Parser for page content. Default: None.
        """
        self._driver: WebDriver = None
        self.options = options
        self.timeout = timeout
        self.headless = headless
        self.cookie_store = cookie_store
        self.browser_storage = browser_storage
        self.soup_maker = soup_maker or SoupMaker()

    def __del__(self):
        if not self._driver:
            return
        self._driver.quit()

    def __enter__(self):
        self._init_browser()
        self._apply_cookies()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if not self._driver:
            return
        self._restore_cookies()
        self._driver.quit()

    def _init_browser(self):
        if self._driver:
            return
        self._driver = create_new(
            options=self.options,
            timeout=self.timeout,
            headless=self.headless,
            soup_maker=self.soup_maker,
        )
        self._driver.implicitly_wait(30)
        self._driver.set_page_load_timeout(30)
        self._action_chain = ActionChains(self._driver)

    def _apply_cookies(self):
        if not self._driver:
            return
        if isinstance(self.cookie_store, RequestsCookieJar):
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
        if isinstance(self.browser_storage, dict):
            for key, value in self.browser_storage['localStorage'].items():
                self._driver.execute_script("window.localStorage.setItem(arguments[0], arguments[1]);", key, value)
            for key, value in self.browser_storage['sessionStorage'].items():
                self._driver.execute_script("window.sessionStorage.setItem(arguments[0], arguments[1]);", key, value)
            logger.debug("Storage applied: %s", self.browser_storage)

    def _restore_cookies(self):
        if not self._driver:
            return
        if isinstance(self.cookie_store, RequestsCookieJar):
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
        if isinstance(self.browser_storage, dict):
            self.browser_storage['localStorage'] = self._driver.execute_script(
                "var ls = window.localStorage, items = {}; "
                "for (var i = 0, k; i < ls.length; ++i) "
                "  items[k = ls.key(i)] = ls.getItem(k); "
                "return items; ")
            self.browser_storage['sessionStorage'] = self._driver.execute_script(
                "var ls = window.sessionStorage, items = {}; "
                "for (var i = 0, k; i < ls.length; ++i) "
                "  items[k = ls.key(i)] = ls.getItem(k); "
                "return items; ")
            logger.debug("Storage retrieved: %s", self.browser_storage)

    @property
    def active(self):
        return check_active(self._driver)

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
    def action_chain(self) -> ActionChains:
        """
        ActionChains are a way to automate low level interactions such as mouse movements,
        mouse button actions, key press, and context menu interactions. This is useful
        for doing more complex actions like hover over and drag and drop.
        """
        return self._action_chain

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
        soup = self.soup_maker.make_soup(self.html)
        setattr(self, "_html_", self.html)
        setattr(self, "_soup_", soup)
        return soup

    def visit(self, url: str) -> None:
        """Visit an URL. Create new session if it does not exist"""
        self._init_browser()
        self._driver.get(url)

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR) -> List[WebElement]:
        if not self._driver:
            return None
        if isinstance(by, By):
            by = str(by)
        return self._driver.find_elements(by, selector)

    def find(self, selector: str, by: By = By.CSS_SELECTOR) -> WebElement:
        if not self._driver:
            return None
        if isinstance(by, By):
            by = str(by)
        return self._driver.find_element(by, selector)

    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        "Select and click on an element."
        if not self._driver:
            return None
        self.find(selector, by).click()

    def submit(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        """Select a form and submit it."""
        if not self._driver:
            return None
        self.find(selector, by).submit()

    def send_keys(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        text: str = "",
        clear: bool = True,
    ) -> None:
        """Select a form and submit it."""
        if not self._driver:
            return None
        elem = self.find(selector, by)
        if clear:
            elem.clear()
        elem.send_keys(text)

    def execute_js(self, script: str, *args, is_async=False) -> Any:
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
            return self._driver.execute_async_script(script, *args)
        else:
            return self._driver.execute_script(script, *args)

    def wait(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: Optional[float] = 30,
        poll_frequency: Optional[float] = 0.25,
        ignored_exceptions: Iterable[Exception] = [],
        expected_conditon=EC.presence_of_element_located,
        reversed: bool = False,
    ):
        """Waits for a element to be visible on the current page by CSS selector.

        Args:
        - chrome: Instance of WebDriver / Browser
        - timeout: Number of seconds before timing out
        - poll_frequency: Sleep interval between calls. Default: 0.5
        - ignored_exceptions: List of exception classes to ignore. Default: [NoSuchElementException]
        - reversed: Wait until the condition not matched
        """
        if not self._driver:
            return
        if not selector or not callable(expected_conditon):
            return
        if isinstance(by, By):
            by = str(by)
        logger.info(
            f"Wait {timeout} seconds for {expected_conditon.__name__} by {by}:{selector}"
        )
        try:
            waiter = WebDriverWait(
                self._driver, timeout, poll_frequency, ignored_exceptions
            )
            if reversed:
                waiter.until_not(expected_conditon((by, selector)))
            else:
                waiter.until(expected_conditon((by, selector)))
        except Exception as e:
            logger.info("Waiting could not be finished | %s", e)
