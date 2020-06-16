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
from glob import glob
from typing import List, Union
from urllib.parse import urlparse

from ... import sources
from .scraper import Scraper

# This list will be auto-generated
scraper_list: List[Scraper] = []


def is_rejected_source(url: str) -> bool:
    host = urlparse(url).netloc
    if host in sources.rejected_sources:
        return True
    return False


def raise_if_rejected(url: str) -> None:
    host = urlparse(url).netloc
    if host in sources.rejected_sources:
        raise Exception(sources.rejected_sources[host])


def get_scraper_by_url(url: str) -> Union[Scraper, None]:
    raise_if_rejected(url)
    parsed_url = urlparse(url)
    for scraper in scraper_list:
        for base_url in scraper.base_urls:
            if urlparse(base_url).netloc == parsed_url.netloc:
                return scraper
    return None


def get_scraper_by_name(name: str) -> Union[Scraper, None]:
    for scraper in scraper_list:
        if getattr(scraper, 'name', '') == name:
            return scraper
    return None


# Auto-import all submodules
re_module = re.compile(r'^([^_.][^.]+).py[c]?$', re.IGNORECASE)
re_url = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)

sources_folder = os.path.abspath(sources.__path__[0])
for file_path in glob(sources_folder + '/**/*.py', recursive=True):
    if not os.path.isfile(file_path):
        continue

    file_name = os.path.basename(file_path)
    regex_result = re_module.match(file_name)
    if not regex_result:  # does not contains a module
        continue

    rel_path = file_path[len(sources_folder) + 1:-3]
    module_name = sources.__package__ + '.' + rel_path.replace(os.sep, '.')
    module = importlib.import_module(module_name, package=__package__)

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
            if re_url.match(url):
                new_base_urls.append(url)

        if len(new_base_urls) == 0:
            raise Exception(key + ': `base_urls` should contain at least one valid url')

        if any([is_rejected_source(url) for url in new_base_urls]):
            continue  # do not add rejected scraper

        scraper_name = module_name.split('.')[-1]
        instance: Scraper = scraper(scraper_name)
        instance.base_urls = new_base_urls
        scraper_list.append(instance)
