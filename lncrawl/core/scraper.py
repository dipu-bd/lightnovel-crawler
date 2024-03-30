import base64
import logging
import os
import random
import ssl
from io import BytesIO
from typing import Any, Dict, Optional, Union
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper, User_Agent
from PIL import Image, UnidentifiedImageError
from requests import Response, Session
from requests.exceptions import ProxyError
from requests.structures import CaseInsensitiveDict

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import ScraperErrorGroup
from .proxy import get_a_proxy, remove_faulty_proxies
from .soup import SoupMaker
from .taskman import TaskManager

logger = logging.getLogger(__name__)


class Scraper(TaskManager, SoupMaker):
    # ------------------------------------------------------------------------- #
    # Initializers
    # ------------------------------------------------------------------------- #
    def __init__(
        self,
        origin: str,
        workers: Optional[int] = None,
        parser: Optional[str] = None,
    ) -> None:
        """Creates a standalone Scraper instance.
        It is primarily being used as a superclass of the Crawler.

        Args:
        - origin (str): The origin URL of the scraper.
        - workers (int, optional): Number of concurrent workers to expect. Default: 10.
        - parser (Optional[str], optional): Desirable features of the parser. This can be the name of a specific parser
            ("lxml", "lxml-xml", "html.parser", or "html5lib") or it may be the type of markup to be used ("html", "html5", "xml").
        """
        self.home_url = origin
        self.last_soup_url = ""
        self.use_proxy = os.getenv("use_proxy")

        self.init_scraper()
        self.change_user_agent()
        self.init_parser(parser)
        self.init_executor(workers)

    def __del__(self) -> None:
        if hasattr(self, "scraper"):
            self.scraper.close()
        super().__del__()

    def init_parser(self, parser: Optional[str] = None):
        self._soup_tool = SoupMaker(parser)
        self.make_tag = self._soup_tool.make_tag
        self.make_soup = self._soup_tool.make_soup

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

    # ------------------------------------------------------------------------- #
    # Internal methods
    # ------------------------------------------------------------------------- #

    def __get_proxies(self, scheme, timeout: int = 0):
        if self.use_proxy and scheme:
            return {scheme: get_a_proxy(scheme, timeout)}
        return {}

    def __process_request(self, method: str, url, **kwargs):
        method_call = getattr(self.scraper, method)
        assert callable(method_call), f"No request method: {method}"

        _parsed = urlparse(url)

        kwargs = kwargs or dict()
        retry = kwargs.pop("retry", 1)
        kwargs.setdefault("allow_redirects", True)
        kwargs["proxies"] = self.__get_proxies(_parsed.scheme)
        headers = kwargs.pop("headers", {})
        headers = CaseInsensitiveDict(headers)
        # headers.setdefault("Host", _parsed.hostname)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.last_soup_url or self.home_url)
        headers.setdefault("User-Agent", self.user_agent)
        kwargs["headers"] = {
            str(k).encode("utf-8"): str(v).encode("utf-8")
            for k, v in headers.items()
            if v
        }

        while retry >= 0:
            try:
                logger.debug(
                    f"[{method.upper()}] {url}\n"
                    + ", ".join([f"{k}={v}" for k, v in kwargs.items()])
                )

                with self.domain_gate(_parsed.hostname):
                    with no_ssl_verification():
                        response: Response = method_call(url, **kwargs)
                        response.raise_for_status()
                        response.encoding = "utf8"

                self.cookies.update({x.name: x.value for x in response.cookies})
                return response
            except ScraperErrorGroup as e:
                if retry == 0:  # retry attempt depleted
                    raise e

                retry -= 1
                logger.debug(f"{type(e).__qualname__}: {e} | Retrying...", e)

                if isinstance(e, ProxyError):
                    for proxy_url in kwargs.get("proxies", {}).values():
                        remove_faulty_proxies(proxy_url)
                    kwargs["proxies"] = self.__get_proxies(_parsed.scheme, 5)

    # ------------------------------------------------------------------------- #
    # Helpers
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
            page_url = str(self.last_soup_url or self.home_url)
        if url.startswith("//"):
            return self.home_url.split(":")[0] + ":" + url
        if url.find("//") >= 0:
            return url
        if url.startswith("/"):
            return self.home_url.strip("/") + url
        if page_url:
            return page_url.strip("/") + "/" + url
        return self.home_url + url

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
    # Downloaders
    # ------------------------------------------------------------------------- #

    def get_response(self, url, retry=1, timeout=(7, 301), **kwargs) -> Response:
        """Fetch the content and return the response"""
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
        self, url, data=None, multipart=False, headers={}, **kwargs
    ) -> Response:
        """Simulate submit form request and return the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Content-Type",
            (
                "multipart/form-data"
                if multipart
                else "application/x-www-form-urlencoded; charset=UTF-8"
            ),
        )
        return self.post_response(url, data=data, headers=headers, **kwargs)

    def download_file(self, url: str, output_file: str, **kwargs) -> None:
        """Download content of the url to a file"""
        response = self.__process_request("get", url, **kwargs)
        with open(output_file, "wb") as f:
            f.write(response.content)

    def download_image(self, url: str, headers={}, **kwargs) -> Image:
        """Download image from url"""
        if url.startswith("data:"):
            content = base64.b64decode(url.split("base64,")[-1])
            return Image.open(BytesIO(content))

        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Origin", None)
        headers.setdefault("Referer", None)

        try:
            response = self.__process_request("get", url, headers=headers, **kwargs)
            content = response.content
            return Image.open(BytesIO(content))

        except UnidentifiedImageError:
            headers.setdefault(
                "Accept",
                "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9",
            )
            response = self.__process_request("get", url, headers=headers, **kwargs)
            content = response.content
            return Image.open(BytesIO(content))

    def get_json(self, url, headers={}, **kwargs) -> Any:
        """Fetch the content and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.get_response(url, headers=headers, **kwargs)
        return response.json()

    def post_json(self, url, data={}, headers={}, **kwargs) -> Any:
        """Make a POST request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.post_response(url, data=data, headers=headers, **kwargs)
        return response.json()

    def submit_form_json(
        self, url, data={}, headers={}, multipart=False, **kwargs
    ) -> Any:
        """Simulate submit form request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.submit_form(
            url, data=data, headers=headers, multipart=multipart, **kwargs
        )
        return response.json()

    def get_soup(self, url, headers={}, encoding=None, **kwargs) -> BeautifulSoup:
        """Fetch the content and return a BeautifulSoup instance of the page"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.get_response(url, headers=headers, **kwargs)
        self.last_soup_url = url
        return self.make_soup(response, encoding)

    def post_soup(
        self, url, data={}, headers={}, encoding=None, **kwargs
    ) -> BeautifulSoup:
        """Make a POST request and return BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.post_response(url, data=data, headers=headers, **kwargs)
        return self.make_soup(response, encoding)

    def submit_form_for_soup(
        self, url, data={}, headers={}, multipart=False, encoding=None, **kwargs
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
        return self.make_soup(response, encoding)
