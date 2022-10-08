from cloudscraper.exceptions import CloudflareException


class LNException(Exception):
    pass


class ScraperNotSupported(CloudflareException):
    pass
