import logging
import os
import random
import ssl
from abc import ABC
from concurrent.futures import ThreadPoolExecutor
from threading import Semaphore
from typing import Dict
from urllib.parse import urlparse

import cloudscraper
from bs4 import BeautifulSoup
from requests import Response, Session
from requests.exceptions import ProxyError, RequestException

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import LNException
from .proxy import get_a_proxy, remove_faulty_proxies

logger = logging.getLogger(__name__)

MAX_WORKER_COUNT = 10
MAX_REQUESTs_PER_DOMAIN = 25
REQUEST_SEMAPHORES: Dict[str, Semaphore] = {}


def _domain_gate(url: str):
    try:
        host = urlparse(url).netloc
    except Exception:
        host = url
    if host not in REQUEST_SEMAPHORES:
        REQUEST_SEMAPHORES[host] = Semaphore(MAX_REQUESTs_PER_DOMAIN)
    return REQUEST_SEMAPHORES[host]


class Scraper(ABC):
    # ------------------------------------------------------------------------- #
    # Constructor method
    # ------------------------------------------------------------------------- #
    def __init__(self) -> None:
        self.init_executor()
        self._destroyed = False
        self.last_visited_url = None

        # Initialize cloudscrapper
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self.scraper = cloudscraper.create_scraper(
                # debug=True,
                ssl_context=ctx,
                browser={
                    "custom": random.choice(user_agents),
                    #'browser': 'chrome',
                    #'platform': 'windows',
                    #'mobile': False
                },
            )
        except Exception:
            logger.exception("Failed to initialize cloudscraper")
            self.scraper = Session()

        # Setup an automatic proxy switcher
        self.enable_auto_proxy = os.getenv("use_proxy") == "1"

    def destroy(self) -> None:
        self._destroyed = True
        self.scraper.close()
        self.executor.shutdown(False)

    # ------------------------------------------------------------------------- #
    # Private methods
    # ------------------------------------------------------------------------- #

    def __generate_proxy(self, url, timeout: int = 0):
        if not self.enable_auto_proxy or not url:
            return None

        scheme = urlparse(self.home_url).scheme
        proxy = {scheme: get_a_proxy(scheme, timeout)}
        return proxy

    def __process_request(self, method: str, url, **kwargs):
        method_call = getattr(self.scraper, method)
        assert callable(method_call), f"No request method: {method}"

        kwargs = kwargs or dict()
        retry = kwargs.pop("retry", 2)
        # kwargs.setdefault('verify', False)
        # kwargs.setdefault('allow_redirects', True)
        headers = kwargs.setdefault("headers", {})
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault("Host", urlparse(self.home_url).hostname)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.novel_url.strip("/"))
        kwargs["proxies"] = self.__generate_proxy(url)

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
                    kwargs["proxies"] = self.__generate_proxy(url, 5)

    # ------------------------------------------------------------------------- #
    # Helper methods to be used
    # ------------------------------------------------------------------------- #

    @property
    def headers(self) -> dict:
        return dict(self.scraper.headers)

    def set_header(self, key: str, value: str) -> None:
        self.scraper.headers[key.lower()] = value

    @property
    def cookies(self) -> dict:
        return {x.name: x.value for x in self.scraper.cookies}

    def set_cookie(self, name: str, value: str) -> None:
        self.scraper.cookies[name] = value

    def absolute_url(self, url, page_url=None) -> str:
        url = (url or "").strip()
        if len(url) > 1000 or url.startswith("data:"):
            return url
        if not page_url:
            page_url = self.last_visited_url
        if not url or len(url) == 0:
            return url
        elif url.startswith("//"):
            return self.home_url.split(":")[0] + ":" + url
        elif url.find("//") >= 0:
            return url
        elif url.startswith("/"):
            return self.home_url.strip("/") + url
        elif page_url:
            return page_url.strip("/") + "/" + url
        else:
            return self.home_url + url

    def is_relative_url(self, url) -> bool:
        page = urlparse(self.novel_url)
        url = urlparse(url)
        return page.hostname == url.hostname and url.path.startswith(page.path)

    def make_soup(self, response, parser=None) -> BeautifulSoup:
        if isinstance(response, Response):
            html = response.content.decode("utf8", "ignore")
        elif isinstance(response, bytes):
            html = response.decode("utf8", "ignore")
        elif isinstance(response, str):
            html = str(response)
        else:
            raise LNException("Could not parse response")

        soup = BeautifulSoup(html, parser or "lxml")
        if not soup.find("body"):
            raise ConnectionError("HTML document was not loaded properly")

        return soup

    def init_executor(self, workers: int = MAX_WORKER_COUNT, wait: bool = False):
        if hasattr(self, "executor"):
            if self.executor._max_workers == workers:
                return
            self.executor.shutdown(wait)
        self.executor = ThreadPoolExecutor(
            max_workers=workers,
            thread_name_prefix="lncrawl_scraper",
            initargs=(self),
        )

    # ------------------------------------------------------------------------- #
    # Downloader methods to be used
    # ------------------------------------------------------------------------- #

    def get_response(self, url, **kwargs) -> Response:
        kwargs = kwargs or dict()
        kwargs.setdefault("retry", 3)
        kwargs.setdefault("timeout", (7, 301))  # in seconds

        result = self.__process_request("get", url, **kwargs)
        self.last_visited_url = url.strip("/")
        return result

    def post_response(self, url, data={}, headers={}, **kwargs) -> Response:
        kwargs = kwargs or dict()
        kwargs.setdefault("retry", 1)
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault("Content-Type", "application/json")
        kwargs["headers"] = headers
        kwargs["data"] = data

        return self.__process_request("post", url, **kwargs)

    def submit_form(self, url, data={}, multipart=False, headers={}) -> Response:
        """Submit a form using post request"""
        if self._destroyed:
            raise LNException("Instance is detroyed")

        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault(
            "Content-Type",
            "multipart/form-data"
            if multipart
            else "application/x-www-form-urlencoded; charset=UTF-8",
        )
        headers.setdefault("Host", urlparse(self.home_url).hostname)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.novel_url.strip("/"))

        return self.post_response(url, data, headers)

    def get_soup(self, url, **kwargs) -> BeautifulSoup:
        """Downloads an URL and make a BeautifulSoup object from response"""
        parser = kwargs.pop("parser", None)
        response = self.get_response(url, **kwargs)
        return self.make_soup(response, parser)

    def get_json(self, *args, **kwargs) -> dict:
        kwargs = kwargs or dict()
        headers = kwargs.setdefault("headers", {})
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault("Accept", "application/json, text/javascript, */*")
        response = self.get_response(*args, **kwargs)
        return response.json()

    def post_soup(self, url, data={}, headers={}, parser="lxml") -> BeautifulSoup:
        response = self.post_response(url, data, headers)
        return self.make_soup(response, parser)

    def post_json(self, url, data={}, headers={}) -> dict:
        headers = {k.lower(): v for k, v in headers.items()}
        headers.setdefault("Accept", "application/json, text/plain, */*")
        response = self.post_response(url, data, headers)
        return response.json()

    def download_file(self, output_file) -> None:
        response = self.get_response(self.novel_cover)
        with open(output_file, "wb") as f:
            f.write(response.content)
