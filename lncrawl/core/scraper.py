import base64
import logging
import os
import tempfile
from io import BytesIO
from pathlib import Path
from typing import Any, MutableMapping, Optional, Tuple, Union

from PIL import Image, UnidentifiedImageError
from requests import Response
from requests.structures import CaseInsensitiveDict

from ..cloudscraper import CloudScraper
from ..context import ctx
from .soup import PageSoup

logger = logging.getLogger(__name__)


class Scraper(CloudScraper):
    def __init__(
        self,
        origin: Optional[str] = None,
        parser: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Initialize the Scraper

        Args:
            origin (Optional[str], default=None): The base URL from which the scraper will operate.
            parser (Optional[str], default=None): The desired parser or markup type.
                - Acceptable values include parser names ("lxml", "lxml-xml", "html.parser", "html5lib")
                - or, markup types ("html", "html5", "xml").
        """
        super().__init__(
            debug=ctx.logger.is_debug,  # Enable for monitoring
            # KEY SETTINGS to prevent 403 errors
            min_request_interval=2.0,  # Prevents TLS blocking
            max_concurrent_requests=1,  # Prevents concurrent conflicts
            rotate_tls_ciphers=True,  # Avoids cipher detection
            # Enhanced protection
            auto_refresh_on_403=False,  # Auto-recover from 403 errors
            max_403_retries=2,  # Max retry attempts
            session_refresh_interval=900,  # Session refresh time in seconds
            # Optimized stealth mode
            enable_stealth=True,
            stealth_options={
                "min_delay": 1.0,  # Minimum delay between requests
                "max_delay": 3.0,  # Maximum delay between requests
                "human_like_delays": True,  # Human-like delays
                "randomize_headers": True,
                "browser_quirks": True,  # Simulate browser like behavior
            },
            # User agent filtering
            browser={
                "browser": "firefox",  # Firefox browser
                "platform": "windows",  # Windows platform
                "desktop": True,  # Desktop environment
                "mobile": False,  # Mobile environment
            },
            **kwargs,
        )

        self.origin = origin or ""
        self.parser = parser or "lxml"

    def set_header(self, key: str, value: Union[str, bytes]) -> None:
        """Set default headers for next requests"""
        self.headers[key] = value

    def set_cookie(self, name: str, value: str) -> None:
        """Set a session cookie"""
        self.cookies.set(name, value)

    def request(self, method, url, *args, **kwargs):
        headers = CaseInsensitiveDict(kwargs.pop("headers", {}) or {})
        headers.setdefault("Origin", self.origin.strip("/"))
        headers.setdefault("Referer", self.origin)
        kwargs["headers"] = headers

        kwargs.setdefault("allow_redirects", True)

        response = super().request(method, url, *args, **kwargs)
        response.raise_for_status()
        response.encoding = "utf8"
        return response

    def ping(self, url: str, timeout=5, **kwargs):
        return self.request("head", url, **kwargs, timeout=timeout)

    def get(self, url, **kwargs):
        kwargs.setdefault("timeout", (7, 301))
        return super().get(url, **kwargs)

    def submit_form(
        self,
        url: str,
        data: Optional[Union[MutableMapping, str, bytes]] = None,
        json: Optional[Union[MutableMapping, str, bytes]] = None,
        headers: MutableMapping = {},
        multipart: bool = False,
        **kwargs,
    ) -> Response:
        if multipart:
            content_type = "multipart/form-data"
        else:
            content_type = "application/x-www-form-urlencoded; charset=UTF-8"

        headers = CaseInsensitiveDict(headers or {})
        headers["Content-Type"] = content_type
        kwargs["headers"] = headers

        return self.post(url, data=data, json=json, **kwargs)

    def get_file(
        self,
        url: str,
        output_file: Union[str, Path],
        headers: MutableMapping = {},
        **kwargs,
    ) -> None:
        """Download content of the url to a file"""
        if isinstance(output_file, str):
            output_file = Path(output_file)

        kwargs["headers"] = headers
        kwargs.setdefault("stream", True)
        response = self.get(url, **kwargs)

        output_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("ab") as tmp:
            for chunk in response.iter_content(chunk_size=10240):
                tmp.write(chunk)
            tmp.flush()
            os.rename(tmp.name, output_file)

    def get_image(
        self,
        url: str,
        headers: MutableMapping = {},
        timeout: Tuple[float, float] = (3, 30),
        **kwargs,
    ) -> Image.Image:
        """Download image from url and return a PIL Image object"""
        if url.startswith("data:"):
            content = base64.b64decode(url.split("base64,")[-1])
            return Image.open(BytesIO(content))

        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Origin", None)
        headers.setdefault("Referer", None)
        kwargs["timeout"] = timeout
        kwargs["headers"] = headers

        try:
            response = self.get(url, **kwargs)
            return Image.open(BytesIO(response.content))
        except UnidentifiedImageError:
            headers.setdefault(
                "Accept",
                "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.9",
            )
            response = self.get(url, **kwargs)
            return Image.open(BytesIO(response.content))

    def get_json(self, url: str, headers: MutableMapping = {}, **kwargs) -> Any:
        """Fetch the content and return the content as a JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Accept", "application/json,text/plain,*/*")
        kwargs["headers"] = headers
        return self.get(url, **kwargs).json()

    def post_json(
        self,
        url: str,
        data: Optional[Union[MutableMapping, str, bytes]] = None,
        headers: MutableMapping = {},
        **kwargs,
    ) -> Any:
        """Make a POST request and return the content as JSON object"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Content-Type", "application/json")
        headers.setdefault("Accept", "application/json,text/plain,*/*")
        response = self.post(url, data=data, headers=headers, **kwargs)
        return response.json()

    def make_soup(
        self,
        data: Union[Response, bytes, str, Any],
        encoding: Optional[str] = None,
    ) -> PageSoup:
        return PageSoup.create(data, encoding, self.parser)

    def get_soup(
        self,
        url: str,
        headers: MutableMapping = {},
        encoding: Optional[str] = None,
        **kwargs,
    ) -> PageSoup:
        """Fetch the content and return a PageSoup instance of the page"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9")
        kwargs["headers"] = headers
        response = self.get(url, **kwargs)
        return self.make_soup(response, encoding)

    def post_soup(
        self,
        url: str,
        data: Optional[Union[MutableMapping, str, bytes]] = None,
        headers: MutableMapping = {},
        encoding: Optional[str] = None,
        **kwargs,
    ) -> PageSoup:
        """Make a POST request and return PageSoup instance of the response"""
        headers = CaseInsensitiveDict(headers)
        headers.setdefault("Accept", "text/html,application/xhtml+xml,application/xml;q=0.9")
        kwargs["headers"] = headers
        response = self.post(url, data=data, **kwargs)
        return self.make_soup(response, encoding)
