import logging
import os
import random
import ssl
import time
from threading import Semaphore
from typing import Dict, Optional, Union
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper, User_Agent
from requests import Response, Session
from requests.exceptions import ProxyError, RequestException
from requests.structures import CaseInsensitiveDict

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import LNException
from .proxy import get_a_proxy, remove_faulty_proxies
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

        self.init_scraper()
        self.change_user_agent()

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
        retry = kwargs.pop("retry", 2)
        kwargs["proxies"] = self.__generate_proxy(url)
        headers = kwargs.pop("headers", {})
        if not isinstance(headers, CaseInsensitiveDict):
            headers = CaseInsensitiveDict(headers)
        headers.setdefault("Host", self.origin.hostname)
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
        url = str(url or "").strip()
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

    def init_scraper(self, sess: Session = None):
        """Check for option: https://github.com/VeNoMouS/cloudscraper"""
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            self.scraper = CloudScraper.create_scraper(
                sess,
                # debug=True,
                delay=10,
                ssl_context=ctx,
                interpreter="js2py",
            )
        except Exception:
            logger.exception("Failed to initialize cloudscraper")
            self.scraper = Session()

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

    def get_response(self, url, **kwargs) -> Response:
        kwargs = kwargs or dict()
        kwargs.setdefault("retry", 3)
        kwargs.setdefault("timeout", (7, 301))  # in seconds

        result = self.__process_request("get", url, **kwargs)
        self.last_visited_url = url.strip("/")
        return result

    def post_response(self, url, data={}, headers={}, **kwargs) -> Response:
        kwargs = kwargs or dict()
        if not isinstance(headers, CaseInsensitiveDict):
            headers = CaseInsensitiveDict(headers)
        kwargs.setdefault("retry", 1)
        headers.setdefault("Content-Type", "application/json")
        kwargs["headers"] = headers
        kwargs["data"] = data
        return self.__process_request("post", url, **kwargs)

    def submit_form(self, url, data={}, multipart=False, headers={}) -> Response:
        """Submit a form using post request"""
        if self._destroyed:
            raise LNException("Instance is detroyed")
        if not isinstance(headers, CaseInsensitiveDict):
            headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Content-Type",
            "multipart/form-data"
            if multipart
            else "application/x-www-form-urlencoded; charset=UTF-8",
        )
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

    def download_file(self, url: str, output_file: str) -> None:
        response = self.get_response(url)
        with open(output_file, "wb") as f:
            f.write(response.content)

    def download_image(self, url: str) -> bytes:
        """Download image from url"""
        logger.info("Downloading image: " + url)
        response = self.get_response(
            url,
            headers={
                "accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9"
            },
        )
        return response.content
