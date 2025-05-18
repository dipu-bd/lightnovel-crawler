import base64
import logging
import os
import random
import ssl
from io import BytesIO
from typing import Any, Callable, Dict, MutableMapping, Optional, Tuple, Union
from urllib.parse import ParseResult, urlparse

from bs4 import BeautifulSoup
from cloudscraper import CloudScraper, User_Agent
from PIL import Image, UnidentifiedImageError
from requests import Response, Session
from requests.exceptions import ProxyError
from requests.structures import CaseInsensitiveDict
from tenacity import (RetryCallState, retry, retry_if_exception_type,
                      stop_after_attempt, wait_random_exponential)

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification
from .exeptions import RetryErrorGroup
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
        """
        Initializes a new instance of the Scraper class.

        This constructor sets up the Scraper, which is typically used as a base class for the
        Crawler. It configures the origin URL, the number of concurrent workers, and the parser
        to use for processing markup.

        Parameters:
            - origin (str): The base URL from which the scraper will operate.
            - workers (Optional[int], default=None): The number of concurrent worker threads or
                processes. If not specified, a default value (typically 10) is used.
            - parser (Optional[str], default=None): The desired parser or markup type.
                - Acceptable values include parser names ("lxml", "lxml-xml", "html.parser", "html5lib")
                - or, markup types ("html", "html5", "xml").

        Side Effects:
            - Sets up internal state, including proxy usage, user agent, parser, and executor
              for concurrent tasks.
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
        self.make_tag = self._soup_tool.make_tag  # type:ignore
        self.make_soup = self._soup_tool.make_soup  # type:ignore

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
                # interpreter="nodejs",
            )
        except Exception:
            logger.exception("Failed to initialize cloudscraper")
            self.scraper = session or Session()

    # ------------------------------------------------------------------------- #
    # Internal methods
    # ------------------------------------------------------------------------- #

    def __get_proxies(self, scheme, timeout: float = 0):
        if self.use_proxy and scheme:
            return {scheme: get_a_proxy(scheme, timeout)}
        return {}

    def __process_request(
        self,
        method: str,
        url: str,
        *args,
        max_retries: Optional[int] = None,
        headers: Optional[MutableMapping] = {},
        **kwargs,
    ):
        method_call: Callable[..., Response] = getattr(self.scraper, method)
        if not callable(method_call):
            raise Exception(f"No request method: {method}")

        _parsed = urlparse(url)

        kwargs = kwargs or dict()
        kwargs.setdefault("allow_redirects", True)
        kwargs["proxies"] = self.__get_proxies(_parsed.scheme)

        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Origin", self.home_url.strip("/"))
        headers.setdefault("Referer", self.last_soup_url or self.home_url)
        headers.setdefault("User-Agent", self.user_agent)

        def _after_retry(retry_state: RetryCallState):
            future = retry_state.outcome
            if future:
                e = future.exception()
                if isinstance(e, RetryErrorGroup):
                    logger.debug(f"{repr(e)} | Retrying...", e)
                    if isinstance(e, ProxyError):
                        for proxy_url in kwargs.get("proxies", {}).values():
                            remove_faulty_proxies(proxy_url)
                        kwargs["proxies"] = self.__get_proxies(_parsed.scheme, 5)

        @retry(
            stop=stop_after_attempt(max_retries or (self.workers + 3)),
            wait=wait_random_exponential(multiplier=0.5, max=60),
            retry=retry_if_exception_type(RetryErrorGroup),
            after=_after_retry,
            reraise=True,
        )
        def _do_request():
            with self.domain_gate(_parsed.hostname):
                with no_ssl_verification():
                    response = method_call(
                        url,
                        *args,
                        **kwargs,
                        headers=headers,
                    )
                    response.raise_for_status()
                    response.encoding = "utf8"

            self.cookies.update({x.name: x.value for x in response.cookies})
            return response

        logger.debug(
            f"[{method.upper()}] {url}\n"
            + "\n".join([f"    {k} = {v}" for k, v in kwargs.items()])
        )
        return _do_request()

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

    def get_response(
        self,
        url: str,
        timeout: Optional[Union[float, Tuple[float, float]]] = (7, 301),
        **kwargs,
    ) -> Response:
        """
        Fetches the content from the specified URL using a GET request and returns the response.

        Parameters:
            - url (str): The full URL to send the GET request to.
            - timeout (Optional[float | Tuple[float, float]]): Timeout setting for the request.
                - If a single float is provided, it is used for both the connect and read timeouts.
                - If a tuple of two floats is provided, the first is used for the connect timeout and the second
                  for the read timeout.
                - Defaults to (7, 301).
            - **kwargs: Additional keyword arguments to pass to the request.

        Returns:
            - Response: The response object resulting from the GET request.
        """
        return self.__process_request(
            "get",
            url,
            timeout=timeout,
            **kwargs,
        )

    def post_response(
        self,
        url: str,
        data: Optional[MutableMapping] = {},
        max_retries: Optional[int] = 0,
        **kwargs
    ) -> Response:
        """Make a POST request and return the response"""
        return self.__process_request(
            "post",
            url,
            data=data,
            max_retries=max_retries,
            **kwargs,
        )

    def submit_form(
        self,
        url: str,
        data: Optional[MutableMapping] = None,
        multipart: bool = False,
        headers: Optional[MutableMapping] = {},
        **kwargs
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

    def download_file(
        self,
        url: str,
        output_file: str,
        **kwargs
    ) -> None:
        """Download content of the url to a file"""
        response = self.__process_request("get", url, **kwargs)
        with open(output_file, "wb") as f:
            f.write(response.content)

    def download_image(
        self,
        url: str,
        headers: Optional[MutableMapping] = {},
        **kwargs
    ):
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

    def get_json(
        self,
        url: str,
        headers: Optional[MutableMapping] = {},
        **kwargs
    ) -> Any:
        """Fetch the content and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.get_response(url, headers=headers, **kwargs)
        return response.json()

    def post_json(
        self,
        url: str,
        data: Optional[MutableMapping] = {},
        headers: Optional[MutableMapping] = {},
        **kwargs,
    ) -> Any:
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
        self,
        url: str,
        data: Optional[MutableMapping] = {},
        headers: Optional[MutableMapping] = {},
        multipart: Optional[bool] = False,
        **kwargs
    ) -> Any:
        """Simulate submit form request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "application/json,text/plain,*/*",
        )
        response = self.submit_form(
            url,
            data=data,
            headers=headers,
            multipart=bool(multipart),
            **kwargs
        )
        return response.json()

    def get_soup(
        self,
        url: str,
        headers: Optional[MutableMapping] = {},
        encoding: Optional[str] = None,
        **kwargs,
    ) -> BeautifulSoup:
        """Fetch the content and return a BeautifulSoup instance of the page"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.get_response(
            url,
            headers=headers,
            **kwargs,
        )
        self.last_soup_url = url
        return self.make_soup(response, encoding)

    def post_soup(
        self,
        url: str,
        data: Optional[MutableMapping] = {},
        headers: Optional[MutableMapping] = {},
        encoding: Optional[str] = None,
        **kwargs
    ) -> BeautifulSoup:
        """Make a POST request and return BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.post_response(
            url,
            data=data,
            headers=headers,
            **kwargs,
        )
        return self.make_soup(response, encoding)

    def submit_form_for_soup(
        self,
        url: str,
        data: Optional[MutableMapping] = {},
        headers: Optional[MutableMapping] = {},
        multipart: Optional[bool] = False,
        encoding: Optional[str] = None,
        **kwargs
    ) -> BeautifulSoup:
        """Simulate submit form request and return a BeautifulSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault(
            "Accept",
            "text/html,application/xhtml+xml,application/xml;q=0.9",
        )
        response = self.submit_form(
            url,
            data=data,
            headers=headers,
            multipart=bool(multipart),
            **kwargs,
        )
        return self.make_soup(response, encoding)
