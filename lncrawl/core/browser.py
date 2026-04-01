import logging
from functools import cached_property
from io import BytesIO
from typing import Any, Callable, Dict, Iterable, List, Optional, Type

from PIL import Image
from requests.cookies import RequestsCookieJar
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.wait import WebDriverWait

from ..context import ctx
from ..exceptions import ScraperErrorGroup
from ..webdriver import ChromeOptions, WebDriver, create_new
from ..webdriver.elements import EC, By, WebElement
from ..webdriver.job_queue import check_active
from .soup import PageSoup
from .template import SoupTemplate

logger = logging.getLogger(__name__)


class Browser:
    def __init__(
        self,
        headless: bool = True,
        timeout: Optional[int] = 120,
        options: Optional[ChromeOptions] = None,
        cookie_store: Optional[RequestsCookieJar] = None,
        browser_storage: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Interface to interact with chrome webdriver.

        Args:
        - headless (bool, optional): True to hide the UI, False to show the UI. Default: True.
        - timeout (Optional[int], optional): Maximum wait duration in seconds for an element to be available. Default: 120.
        - options (Optional[&quot;ChromeOptions&quot;], optional): Webdriver options. Default: None.
        - cookie_store (Optional[RequestsCookieJar], optional): A cookie store to synchronize cookies. Default: None.
        - browser_storage (Optional[Dict[str, Any]], optional): A Storage to save some user info that is saved in your Browser storage. Default: None.
        - soup_parser (Optional[str], optional): Parser for page content. Default: None.
        """
        self.options = options
        self.timeout = timeout
        self.headless = headless
        self.cookie_store = cookie_store
        self.browser_storage = browser_storage
        self._driver: Optional[WebDriver] = None

    def __del__(self):
        self.close()

    def __enter__(self):
        self.open_browser()
        self.apply_cookies()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.restore_cookies()
        self.close()

    def close(self):
        if not self._driver:
            return
        self._driver.quit()

    def open_browser(self):
        if self._driver:
            return
        self._driver = create_new(
            options=self.options,
            timeout=self.timeout,
            headless=self.headless,
        )
        self._driver.implicitly_wait(30)
        self._driver.set_page_load_timeout(30)
        self._action_chain = ActionChains(self._driver)

    def apply_cookies(self):
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
            for name, raw_store in self.browser_storage.items():
                if not isinstance(raw_store, dict):
                    continue
                self._driver.execute_script(
                    f"arguments.forEach(function(item) {{  window.{name}.setItem(item[0], item[1]);}});",
                    *raw_store.items(),
                )
            logger.debug("Storage applied: %s", self.browser_storage)

    def restore_cookies(self):
        if not self._driver:
            return
        if isinstance(self.cookie_store, RequestsCookieJar):
            for cookie in self._driver.get_cookies():
                name = cookie.get("name")
                value = cookie.get("value")
                if name and value:
                    self.cookie_store.set(
                        name=name,
                        value=value,
                        path=cookie.get("path"),
                        domain=cookie.get("domain"),
                        secure=cookie.get("secure"),
                        expires=cookie.get("expiry"),
                    )
            logger.debug("Cookies retrieved: %s", self.cookie_store)
        if isinstance(self.browser_storage, dict):
            for name in ["localStorage", "sessionStorage"]:
                self.browser_storage[name] = self._driver.execute_script(
                    "var items = {};"
                    f"var ls = window.{name};"
                    "Object.keys(ls).forEach(function(key) {"
                    "  items[key] = ls[key];"
                    "});"
                    "return items;"
                )
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
    def soup(self) -> PageSoup:
        """Get the current page soup"""
        # Return from cache if available
        old_html = getattr(self, "_html_", None)
        if old_html == self.html:
            return getattr(self, "_soup_")
        # Create new soup and save to cache
        soup = PageSoup.create(self.html)
        setattr(self, "_html_", self.html)
        setattr(self, "_soup_", soup)
        return soup

    def visit(self, url: str) -> None:
        """Visit an URL. Create new session if it does not exist"""
        self.open_browser()
        if self._driver:
            return self._driver.get(url)

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR) -> List[WebElement]:
        if not self._driver:
            return []
        return [
            WebElement(self._driver, el) for el in self._driver.find_elements(str(by), selector)
        ]

    def find(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[WebElement]:
        if not self._driver:
            return None
        return WebElement(
            self._driver,
            self._driver.find_element(str(by), selector),
        )

    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        "Select and click on an element."
        if not self._driver:
            return None
        elem = self.find(selector, by)
        if elem:
            elem.scroll_into_view()
            elem.click()

    def submit(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        """Select a form and submit it."""
        if not self._driver:
            return None
        elem = self.find(selector, by)
        if elem:
            elem.scroll_into_view()
            elem.submit()

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
        if elem:
            elem.scroll_into_view()
            if clear:
                elem.clear()
            elem.send_keys(text)

    def execute_js(self, script: str, *args, is_async: bool = False) -> Any:
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
        ignored_exceptions: Optional[Iterable[Type[Exception]]] = None,
        expected_conditon: Callable[..., Any] = EC.presence_of_element_located,
        inverse: bool = False,
    ):
        """Waits for a element to be visible on the current page by CSS selector.

        Args:
        - chrome: Instance of WebDriver / Browser
        - timeout: Number of seconds before timing out
        - poll_frequency: Sleep interval between calls. Default: 0.5
        - ignored_exceptions: List of exception classes to ignore. Default: [NoSuchElementException]
        - inverse: Wait until the condition is not matched
        """
        if not self._driver:
            return
        if not selector or not callable(expected_conditon):
            return
        logger.info(f"Wait {timeout} seconds for {expected_conditon.__name__} by {by}:{selector}")
        try:
            waiter = WebDriverWait(
                self._driver,
                timeout or 30,
                poll_frequency or 0.25,
                ignored_exceptions=ignored_exceptions,
            )
            condition = expected_conditon((str(by), selector))
            if inverse:
                waiter.until_not(condition)  # type: ignore
            else:
                waiter.until(condition)  # type: ignore
        except Exception as e:
            logger.info("Waiting could not be finished | %s", e)


class BrowserTemplate(SoupTemplate):
    """Attempts to crawl using scraper first, on failure use the browser."""

    def __init__(
        self,
        origin: str,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
        headless: bool = False,
        timeout: Optional[int] = 120,
    ) -> None:
        super().__init__(
            origin=origin,
            workers=workers,
            parser=parser,
        )
        self.timeout = timeout
        self.headless = headless
        self._override_scraper_get_soup()
        self._override_scraper_get_image()

    def _override_scraper_get_soup(self) -> None:
        origin_method = self.scraper.get_soup

        def get_soup(url, *args, **kwargs):
            try:
                return origin_method(url, *args, **kwargs)
            except ScraperErrorGroup:
                if ctx.logger.is_debug:
                    ctx.logger.error("Failed to get soup", exc_info=True)
                self.browser.visit(url)
                self.browser.wait("body", By.TAG_NAME)
                return self.browser.soup

        setattr(self.scraper, "get_soup", get_soup)

    def _override_scraper_get_image(self) -> None:
        origin_method = self.scraper.get_image

        def get_image(url, *args, **kwargs):
            try:
                return origin_method(url, *args, **kwargs)
            except ScraperErrorGroup:
                if ctx.logger.is_debug:
                    ctx.logger.error("Failed to get image", exc_info=True)
                self.browser.visit(url)
                self.browser.wait("img", By.TAG_NAME)
                img = self.browser.find("img", By.TAG_NAME)
                assert img, "No img element"
                png = img.screenshot_as_png
                return Image.open(BytesIO(png))

        setattr(self.scraper, "get_image", get_image)

    @property
    def using_browser(self) -> bool:
        return "browser" in self.__dict__ and self.browser.active

    @cached_property
    def browser(self) -> Browser:
        """
        A webdriver based browser.
        Requires Google Chrome to be installed.
        """
        if not ctx.config.crawler.can_use_browser:
            raise RuntimeError("Browser is disabled in the configuration")

        _max_workers = self.taskman.workers
        self.taskman.init_executor(1)

        browser = Browser(
            headless=self.headless,
            timeout=self.timeout,
            cookie_store=self.scraper.cookies,
        )

        _visit = browser.visit
        _close = browser.close

        def override_visit(url: str) -> None:
            _visit(url)
            browser.restore_cookies()

        def override_close() -> None:
            _close()
            self.__dict__.pop("browser", None)
            self.taskman.init_executor(_max_workers)

        setattr(browser, "visit", override_visit)
        setattr(browser, "close", override_close)

        return browser

    def close(self) -> None:
        super().close()
        if self.using_browser:
            self.browser.close()

    def visit(self, url: str) -> None:
        self.browser.visit(url)
