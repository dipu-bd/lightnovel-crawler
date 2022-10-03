import logging
import os
import random
import ssl
import time
from threading import Semaphore
from typing import Dict, Optional, Union
from urllib.parse import ParseResult, urlparse

from box import Box
from bs4 import BeautifulSoup
from cloudscraper import CloudScraper, User_Agent
from requests import Response, Session
from requests.exceptions import ProxyError, RequestException
from requests.structures import CaseInsensitiveDict

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .browser import Browser
from .exeptions import LNException
from .proxy import get_a_proxy, remove_faulty_proxies
from .soup import SoupMaker
from .taskman import TaskManager

logger = logging.getLogger(__name__)

MAX_REQUESTS_PER_DOMAIN = 25
REQUEST_SEMAPHORES: Dict[str, Semaphore] = {}


def _domain_gate(url: str = ""):
    try:
        host = url.split("//", 1)[1].split("/", 1)[0]
    except Exception:
        host = str(url or "").split("/", 1)[0]
    if host not in REQUEST_SEMAPHORES:
        REQUEST_SEMAPHORES[host] = Semaphore(MAX_REQUESTS_PER_DOMAIN)
    return REQUEST_SEMAPHORES[host]


class Scraper(TaskManager):
    # ------------------------------------------------------------------------- #
    # Constructor & Destructors
    # ------------------------------------------------------------------------- #
    def __init__(self, origin: str) -> None:
        super(Scraper, self).__init__()

        self.home_url = origin
        self.last_visited_url = ""
        self.enable_auto_proxy = os.getenv("use_proxy") == "1"

        self.browser = Browser()
        self.init_scraper()
        self.change_user_agent()

        self._soup_tool = SoupMaker()
        self.make_soup = self._soup_tool.make_soup

    def destroy(self) -> None:
        super(Scraper, self).destroy()
        self.scraper.close()

    # ------------------------------------------------------------------------- #
    # Private methods
    # ------------------------------------------------------------------------- #

    def __generate_proxy(self, url, timeout: int = 0):
        if self.enable_auto_proxy and url:
            scheme = self.origin.scheme
            proxy = {scheme: get_a_proxy(scheme, timeout)}
            return proxy

    def __process_request(self, method: str, url, **kwargs):
        method_call = getattr(self.scraper, method)
        assert callable(method_call), f"No request method: {method}"

        kwargs = kwargs or dict()
        retry = kwargs.pop("retry", 1)
        kwargs["proxies"] = self.__generate_proxy(url)
        headers = kwargs.pop("headers", {})
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Host", urlparse(url).hostname)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.last_visited_url.strip("/"))
        headers.setdefault("User-Agent", self.user_agent)
        kwargs["headers"] = dict(headers)

        while retry >= 0:
            if self._destroyed:
                raise LNException("Instance is detroyed")

            try:
                logger.debug(
                    "[%s] %s\n%s",
                    method.upper(),
                    url,
                    ", ".join([f"{k}={v}" for k, v in kwargs.items()]),
                )

                with _domain_gate(url):
                    with no_ssl_verification():
                        response: Response = method_call(url, **kwargs)

                response.raise_for_status()
                response.encoding = "utf8"
                self.cookies.update({x.name: x.value for x in response.cookies})
                return response
            except RequestException as e:
                if retry == 0:  # retry attempt depleted
                    raise e

                logger.debug("%s | Retrying...", e)
                retry -= 1
                if isinstance(e, ProxyError):
                    for proxy_url in kwargs.get("proxies", {}).values():
                        remove_faulty_proxies(proxy_url)

                if retry != 0:  # do not use proxy on last attemp
                    if self.enable_auto_proxy and url:
                        kwargs["proxies"] = self.__generate_proxy(url, 5)
                    else:
                        time.sleep(2)
                    self.change_user_agent()
                    headers.setdefault("User-Agent", self.user_agent)
                    kwargs["headers"] = dict(headers)

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #

    @property
    def origin(self) -> ParseResult:
        """Parsed self.home_url"""
        return urlparse(self.home_url)

    @property
    def headers(self) -> Dict[str, Union[str, bytes]]:
        """Default request headers"""
        return dict(self.scraper.headers)

    def set_header(self, key: str, value: str) -> None:
        """Set default headers for next requests"""
        self.scraper.headers[key] = value

    @property
    def cookies(self) -> Dict[str, Optional[str]]:
        """Current session cookies"""
        return {x.name: x.value for x in self.scraper.cookies}

    def set_cookie(self, name: str, value: str) -> None:
        """Set a session cookie"""
        self.scraper.cookies.set(name, value)

    def absolute_url(self, url: str, page_url: Optional[str] = None) -> str:
        url = str(url or "").strip().rstrip("/")
        if not url:
            return url
        if len(url) >= 1024 or url.startswith("data:"):
            return url
        if not page_url:
            page_url = str(self.last_visited_url or self.home_url)
        if url.startswith("//"):
            return self.home_url.split(":")[0] + ":" + url
        if url.find("//") >= 0:
            return url
        if url.startswith("/"):
            return self.home_url.strip("/") + url
        if page_url:
            return page_url.strip("/") + "/" + url
        return self.home_url + url

    def init_scraper(self, session: Optional[Session] = None):
        """Check for option: https://github.com/VeNoMouS/cloudscraper"""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self.scraper = CloudScraper.create_scraper(
                session,
                # debug=True,
                # delay=10,
                ssl_context=ctx,
                interpreter="js2py",
            )
        except Exception:
            logger.exception("Failed to initialize cloudscraper")
            self.scraper = session or Session()
        finally:
            self.browser.cookie_store = self.scraper.cookies

    def change_user_agent(self):
        self.user_agent = random.choice(user_agents)
        if isinstance(self.scraper, CloudScraper):
            self.scraper.user_agent = User_Agent(
                allow_brotli=self.scraper.allow_brotli,
                browser={"custom": self.user_agent},
            )
        elif isinstance(self.scraper, Session):
            self.set_header("User-Agent", self.user_agent)

    # ------------------------------------------------------------------------- #
    # Downloader methods to be used
    # ------------------------------------------------------------------------- #

    def get_response(self, url, retry=1, timeout=(7, 301), **kwargs) -> Response:
        """Fetch the content and return the response"""
        self.last_visited_url = url.strip("/")
        return self.__process_request(
            "get",
            url,
            retry=retry,
            timeout=timeout,
            **kwargs,
        )

    def post_response(self, url, data={}, retry=1, **kwargs) -> Response:
        """Make a POST request and return the response"""
        return self.__process_request(
            "post",
            url,
            data=data,
            retry=retry,
            **kwargs,
        )

    def submit_form(
        self, url, data={}, multipart=False, headers={}, **kwargs
    ) -> Response:
        """Simulate submit form request and return the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Content-Type",
            "multipart/form-data"
            if multipart
            else "application/x-www-form-urlencoded; charset=UTF-8",
        )
        return self.post_response(url, data=data, headers=headers, **kwargs)

    def download_file(self, url: str, output_file: str, **kwargs) -> None:
        """Download content of the url to a file"""
        response = self.__process_request("get", url, **kwargs)
        with open(output_file, "wb") as f:
            f.write(response.content)

    def download_image(self, url: str, headers={}, **kwargs) -> bytes:
        """Download image from url"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9",
        )
        response = self.__process_request("get", url, headers=headers, **kwargs)
        return response.content

    def get_json(self, url, headers={}, **kwargs) -> Box:
        """Fetch the content and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.get_response(url, headers=headers, **kwargs)
        return Box(response.json())

    def post_json(self, url, data={}, headers={}) -> Box:
        """Make a POST request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.post_response(url, data=data, headers=headers)
        return Box(response.json())

    def submit_form_json(
        self, url, data={}, headers={}, multipart=False, **kwargs
    ) -> Box:
        """Simulate submit form request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.submit_form(
            url, data=data, headers=headers, multipart=multipart, **kwargs
        )
        return Box(response.json())

    def get_soup(self, url, headers={}, parser=None, **kwargs) -> BeautifulSoup:
        """Fetch the content and return a BeautifulSoup instance of the page"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.get_response(url, **kwargs)
        return self.make_soup(response, parser)

    def post_soup(
        self, url, data={}, headers={}, parser=None, **kwargs
    ) -> BeautifulSoup:
        """Make a POST request and return BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.post_response(url, data=data, headers=headers, **kwargs)
        return self.make_soup(response, parser)

    def submit_form_for_soup(
        self, url, data={}, headers={}, multipart=False, parser=None, **kwargs
    ) -> BeautifulSoup:
        """Simulate submit form request and return a BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.submit_form(
            url, data=data, headers=headers, multipart=multipart, **kwargs
        )
        return self.make_soup(response, parser)
