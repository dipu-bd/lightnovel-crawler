# -*- coding: utf-8 -*-
"""
Auto imports all crawlers from the current package directory.
To be recognized, your crawler file should meet following conditions:
    - file does not starts with an underscore
    - file ends with .py extension
    - file contains a class that extends `app.scraper.scraper.Scraper`
    - the class extending `app.scraper.scraper.Scraper` has a global variable `base_urls`
    - `base_urls` contains a list of urls supported by the crawler

For example, see any of the files inside this directory.
"""

import importlib
import os
import re
import sys
from typing import List, Union, Mapping
from urllib.parse import urlparse

from ..app.scraper.scraper import Scraper

# This list will be auto-generated
scraper_list: List[Scraper] = []

# Add rejected urls with reason here
rejected_sources: Mapping[str, str] = {}


def is_rejected_source(url: str) -> bool:
    host = urlparse(url).netloc
    if host in rejected_sources:
        return True
    return False


def raise_if_rejected(url: str) -> None:
    host = urlparse(url).netloc
    if host in rejected_sources:
        raise Exception(rejected_sources[host])


def get_scraper_by_url(url: str) -> Union[Scraper, None]:
    raise_if_rejected(url)
    parsed_url = urlparse(url)
    hostname = parsed_url.scheme + '//' + parsed_url.netloc
    for scraper in scraper_list:
        for base_hostname in scraper.base_urls:
            if base_hostname == hostname:
                return scraper
    return None


def get_scraper_by_name(name: str) -> Union[Scraper, None]:
    for scraper in scraper_list:
        if scraper.__name__ == name:
            return scraper
    return None


# Auto-import all submodules in the current directory
_module_regex = re.compile(r'^([^_.][^.]+).py[c]?$', re.IGNORECASE)
_url_regex = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)

for entry in os.listdir(__path__[0]):
    file_path = os.path.join(__path__[0], entry)
    if not os.path.isfile(file_path):
        continue

    regex_result = _module_regex.match(entry)
    if regex_result.groupcount() != 1:  # does not contains a module
        continue

    module_name = regex_result.group(1)
    module = importlib.import_module('.' + module_name, package=__package__)

    for key in dir(module):
        scraper = getattr(module, key)
        if type(scraper) != type(Scraper) or scraper.__base__ != Scraper:
            continue

        base_urls = getattr(scraper, 'base_urls')
        if not isinstance(base_urls, list):
            raise Exception(key + ': `base_urls` should be a list of strings')

        new_base_urls = []
        for url in base_urls:
            url = url.strip().strip('/')
            if _url_regex.match(url):
                new_base_urls.append(url)

        if len(new_base_urls) == 0:
            raise Exception(key + ': `base_urls` should contain at least one valid url')

        if any([is_rejected_source(url) for url in new_base_urls]):
            continue  # do not add rejected scraper

        instance: Scraper = scraper(scraper.__name__)
        instance.base_urls = new_base_urls
        scraper_list.append(instance)
