import asyncio
import base64
from enum import Enum
import logging
from typing import TYPE_CHECKING, Any, List, Optional

from requests.cookies import RequestsCookieJar

from ..context import ctx
from ..utils.async_loop import run_async
from ..webdriver import create_new
from ..webdriver.storage import BrowserStorage
from .soup import PageSoup

if TYPE_CHECKING:
    from nodriver import Browser as UCBrowser, Element, Tab

logger = logging.getLogger(__name__)

# ----------------------------------------------------------------------------- #
# Selector helpers
# ----------------------------------------------------------------------------- #

_xpath_seq = 0


class By(str, Enum):
    ID = "id"
    XPATH = "xpath"
    LINK_TEXT = "link text"
    PARTIAL_LINK_TEXT = "partial link text"
    NAME = "name"
    TAG_NAME = "tag name"
    CLASS_NAME = "class name"
    CSS_SELECTOR = "css selector"

    def __str__(self) -> str:
        return self.value


def _to_css(selector: str, by: By) -> str:
    if by == By.CSS_SELECTOR:
        return selector
    elif by == By.ID:
        return f"#{selector}"
    elif by == By.CLASS_NAME:
        return f".{selector}"
    elif by == By.TAG_NAME:
        return selector
    elif by == By.NAME:
        return f"[name='{selector}']"
    else:
        raise ValueError(f"Cannot convert {by} to CSS selector")


async def _tab_find(
    tab: "Tab",
    selector: str,
    by: By,
    timeout: float = 0,
) -> Optional["Element"]:
    try:
        if by == By.XPATH:
            results = await tab.xpath(selector)
            return results[0] if results else None
        elif by == By.LINK_TEXT:
            return await tab.find(selector, best_match=True, timeout=timeout)
        elif by == By.PARTIAL_LINK_TEXT:
            return await tab.find(selector, best_match=False, timeout=timeout)
        else:
            return await tab.select(_to_css(selector, by), timeout=timeout)
    except Exception:
        return None


async def _tab_find_all(
    tab: "Tab",
    selector: str,
    by: By,
) -> List["Element"]:
    try:
        if by == By.XPATH:
            results = await tab.xpath(selector)
            return [e for e in results if e]
        elif by in (By.LINK_TEXT, By.PARTIAL_LINK_TEXT):
            result = await tab.find(selector, best_match=(by == By.LINK_TEXT), timeout=0)
            return [result] if result else []
        else:
            return await tab.select_all(_to_css(selector, by))
    except Exception:
        return []


async def _elem_find_xpath(
    tab: "Tab",
    nd_elem: "Element",
    xpath: str,
) -> Optional["Element"]:
    global _xpath_seq
    _xpath_seq += 1
    attr = f"data-nd-xp-{_xpath_seq}"
    escaped = xpath.replace("\\", "\\\\").replace("'", "\\'")

    await nd_elem.apply(
        f"""function() {{
            var r = document.evaluate('{escaped}', this, null,
                XPathResult.FIRST_ORDERED_NODE_TYPE, null);
            if (r.singleNodeValue) r.singleNodeValue.setAttribute('{attr}', '');
        }}"""
    )
    found = await tab.select(f"[{attr}]")
    if found:
        await found.apply(f"function() {{ this.removeAttribute('{attr}'); }}")
    return found


async def _elem_find_xpath_all(
    tab: "Tab",
    nd_elem: "Element",
    xpath: str,
) -> List["Element"]:
    global _xpath_seq
    _xpath_seq += 1
    attr = f"data-nd-xpa-{_xpath_seq}"
    escaped = xpath.replace("\\", "\\\\").replace("'", "\\'")

    await nd_elem.apply(
        f"""function() {{
            var r = document.evaluate('{escaped}', this, null,
                XPathResult.ORDERED_NODE_ITERATOR_TYPE, null);
            var node;
            while ((node = r.iterateNext())) {{
                node.setAttribute('{attr}', '');
            }}
        }}"""
    )
    results = await tab.select_all(f"[{attr}]")
    for el in results:
        await el.apply(f"function() {{ this.removeAttribute('{attr}'); }}")
    return results


# ----------------------------------------------------------------------------- #
# WebElement
# ----------------------------------------------------------------------------- #


class WebElement:
    def __init__(self, tab: "Tab", elem: "Element") -> None:
        self._tab = tab
        self._elem = elem

    @property
    def text(self) -> str:
        return self._elem.text or ""

    @property
    def tag_name(self) -> str:
        return self._elem.tag_name or ""

    def get_attribute(self, name: str) -> Optional[str]:
        return self._elem[name]

    @property
    def outer_html(self) -> str:
        return run_async(self._elem.get_html()) or ""

    def as_tag(self) -> PageSoup:
        html = self.outer_html
        if not hasattr(self, "_cached_html") or self._cached_html != html:
            self._cached_html = html
            self._cached_tag = PageSoup.create(html)
        return self._cached_tag  # type: ignore[return-value]

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR) -> List["WebElement"]:
        if by == By.XPATH:
            elements = run_async(_elem_find_xpath_all(self._tab, self._elem, selector))
        else:
            elements = run_async(self._elem.query_selector_all(_to_css(selector, by))) or []
        return [WebElement(self._tab, e) for e in elements]

    def find(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional["WebElement"]:
        from nodriver import Element

        if by == By.XPATH:
            nd_elem = run_async(_elem_find_xpath(self._tab, self._elem, selector))
        else:
            result = run_async(self._elem.query_selector(_to_css(selector, by)))
            nd_elem = result if isinstance(result, Element) else None
        return WebElement(self._tab, nd_elem) if nd_elem else None

    def click(self) -> None:
        run_async(self._elem.click())

    def send_keys(self, text: str) -> None:
        run_async(self._elem.send_keys(text))

    def clear(self) -> None:
        run_async(self._elem.clear_input())

    def submit(self) -> None:
        run_async(
            self._elem.apply(
                "function() { var f = this.form || this.closest('form'); if (f) f.submit(); }"
            )
        )

    def remove(self) -> None:
        run_async(self._elem.apply("function() { this.remove(); }"))

    def scroll_into_view(self) -> None:
        run_async(self._elem.apply("function() { this.scrollIntoViewIfNeeded(); }"))

    @property
    def screenshot_as_png(self) -> bytes:
        from nodriver.cdp import page as cdp_page

        _box = run_async(
            self._elem.apply(
                """function() {
                    var r = this.getBoundingClientRect();
                    return {x: r.left, y: r.top, width: r.width, height: r.height};
                }"""
            )
        )
        box: dict = _box if isinstance(_box, dict) else {}
        try:
            if box.get("width") and box.get("height"):
                clip = cdp_page.Viewport(
                    x=box["x"],
                    y=box["y"],
                    width=box["width"],
                    height=box["height"],
                    scale=1,
                )
                data = run_async(
                    self._tab.send(cdp_page.capture_screenshot(format_="png", clip=clip))
                )
                return base64.b64decode(data)
        except Exception:
            pass
        data = run_async(self._tab.send(cdp_page.capture_screenshot(format_="png")))
        return base64.b64decode(data)


# ----------------------------------------------------------------------------- #
# Browser
# ----------------------------------------------------------------------------- #


class Browser:
    def __init__(
        self,
        headless: bool = False,
        timeout: Optional[int] = 120,
        extra_args: Optional[List[str]] = None,
        cookie_store: Optional[RequestsCookieJar] = None,
    ) -> None:
        self.extra_args = extra_args
        self.timeout = timeout
        self.headless = headless
        self.cookie_store = cookie_store
        self._tab: Optional["Tab"] = None
        self._browser: Optional["UCBrowser"] = None
        self.local_storage = BrowserStorage(self, "localStorage")
        self.session_storage = BrowserStorage(self, "sessionStorage")

    def __del__(self) -> None:
        self.close()

    def __enter__(self) -> "Browser":
        self.open_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.close()

    def close(self) -> None:
        if not self._browser:
            return
        ctx.logger.debug("Closing browser")
        try:
            self._browser.stop()
        except Exception:
            pass
        self._browser = None
        self._tab = None

    def open_browser(self) -> None:
        if self._browser:
            return
        ctx.logger.debug("Opening browser")

        self._browser = create_new(
            extra_args=self.extra_args,
            timeout=self.timeout,
            headless=self.headless,
        )
        # Navigate to blank page so we have an active tab for cookie and JS ops
        self._tab = run_async(self._browser.get("about:blank"), timeout=self.timeout)

    @property
    def active(self) -> bool:
        from ..webdriver.job_queue import check_active

        return check_active(self._browser)

    @property
    def current_url(self) -> Optional[str]:
        if not self._tab:
            return None
        return self._tab.url

    @property
    def session_id(self) -> Optional[str]:
        if not self._tab:
            return None
        return getattr(self._tab, "target_id", None)

    @property
    def html(self) -> str:
        if not self._tab:
            return ""
        try:
            return run_async(self._tab.get_content(), timeout=self.timeout) or ""
        except Exception:
            return ""

    @property
    def soup(self) -> PageSoup:
        old_html = getattr(self, "_html_", None)
        current = self.html
        if old_html == current:
            return getattr(self, "_soup_")  # type: ignore[return-value]
        soup = PageSoup.create(current)
        setattr(self, "_html_", current)
        setattr(self, "_soup_", soup)
        return soup

    def visit(self, url: str) -> None:
        self.open_browser()
        if self._browser:
            self._tab = run_async(self._browser.get(url), timeout=self.timeout)

    def find_all(self, selector: str, by: By = By.CSS_SELECTOR) -> List[WebElement]:
        if not self._tab:
            return []
        elements = run_async(_tab_find_all(self._tab, selector, by), timeout=self.timeout)
        return [WebElement(self._tab, e) for e in elements]

    def find(self, selector: str, by: By = By.CSS_SELECTOR) -> Optional[WebElement]:
        if not self._tab:
            return None
        nd_elem = run_async(_tab_find(self._tab, selector, by, timeout=0), timeout=self.timeout)
        return WebElement(self._tab, nd_elem) if nd_elem else None

    def click(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
        elem = self.find(selector, by)
        if elem:
            elem.scroll_into_view()
            elem.click()

    def submit(self, selector: str, by: By = By.CSS_SELECTOR) -> None:
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
        elem = self.find(selector, by)
        if elem:
            elem.scroll_into_view()
            if clear:
                elem.clear()
            elem.send_keys(text)

    def execute_js(self, script: str, is_async: bool = False) -> Any:
        """Execute JavaScript in the current page. Use await_promise for async scripts."""
        if not self._tab:
            return None
        try:
            return run_async(
                self._tab.evaluate(script, await_promise=is_async),
                timeout=self.timeout,
            )
        except Exception as e:
            ctx.logger.debug("execute_js error | %s", e)
            return None

    def wait(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: Optional[float] = None,
        poll_frequency: Optional[float] = 0.25,
        inverse: bool = False,
    ) -> None:
        """Wait until an element matching selector appears (or disappears if inverse=True)."""
        if not self._tab or not selector:
            return
        wait_secs = float(timeout or 60)
        ctx.logger.debug("Wait %.1fs for %s:%s (inverse=%s)", wait_secs, by, selector, inverse)

        try:
            if by == By.XPATH:
                run_async(
                    self._wait_xpath(
                        selector, wait_secs, bool(inverse), float(poll_frequency or 0.25)
                    ),
                    timeout=wait_secs + 5,
                )
            else:
                if inverse:
                    run_async(
                        self._wait_css_gone(selector, by, wait_secs, float(poll_frequency or 0.25)),
                        timeout=wait_secs + 5,
                    )
                else:
                    run_async(
                        _tab_find(self._tab, selector, by, timeout=wait_secs),
                        timeout=wait_secs + 5,
                    )
        except Exception as e:
            ctx.logger.info("wait() did not finish cleanly | %s", e)

    async def _wait_xpath(self, selector: str, timeout: float, inverse: bool, poll: float) -> None:
        assert self._tab is not None
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            results = await self._tab.xpath(selector)
            if (not inverse and results) or (inverse and not results):
                return
            await asyncio.sleep(poll)

    async def _wait_css_gone(self, selector: str, by: By, timeout: float, poll: float) -> None:
        assert self._tab is not None
        deadline = asyncio.get_event_loop().time() + timeout
        while asyncio.get_event_loop().time() < deadline:
            elem = await _tab_find(self._tab, selector, by, timeout=0)
            if not elem:
                return
            await asyncio.sleep(poll)
