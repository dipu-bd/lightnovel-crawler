from urllib.error import URLError

from cloudscraper.exceptions import CloudflareException
from requests.exceptions import RequestException
from urllib3.exceptions import HTTPError


class LNException(Exception):
    pass


class FallbackToBrowser(Exception):
    pass


ScraperErrorGroup = (
    URLError,
    HTTPError,
    CloudflareException,
    RequestException,
    FallbackToBrowser,
)
