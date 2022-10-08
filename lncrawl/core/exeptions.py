from urllib.error import URLError

from cloudscraper.exceptions import CloudflareException
from requests.exceptions import RequestException


class LNException(Exception):
    pass


class FallbackToBrowser(Exception):
    pass


ScraperErrorGroup = (
    URLError,
    CloudflareException,
    RequestException,
    FallbackToBrowser,
)
