# -*- coding: utf-8 -*-
"""
Auto imports all crawlers from the current package directory.
To be recognized, your crawler file should meet following conditions:
    - file does not starts with an underscore
    - file ends with .py extension
    - file contains a class that extends `src.utils.crawler.Crawler`
    - the class extending `src.utils.crawler.Crawler` has a global variable `base_url`
    - `base_url` contains a valid url or a list of urls supported by the crawler

For example, see any of the files inside this directory.
"""

import importlib
import os
import re
import sys
from urllib.parse import urlparse

from ..utils.crawler import Crawler

rejected_sources = {
    'http://fullnovel.live/': "403 - Forbidden: Access is denied",
    'http://moonbunnycafe.com/': "Does not follow uniform format",
    'https://indomtl.com/': "Does not like to be crawled",
    'https://lnindo.org/': "Does not like to be crawled",
    'https://myoniyonitranslations.com/': "522 - Connection timed out",
    'https://novelgo.id/': "Removed by owner",
    'https://novelsrock.com/': '404 - Not Found',
    'https://www.flying-lines.com/': 'Obfuscated content',
    'https://www.jieruihao.cn/': "Unavailable",
    'https://www.noveluniverse.com/': "Site is down",
    'https://www.novelupdates.com/': "Does not host any novels",
    'https://www.novelv.com/': "Site is down",
    'https://yukinovel.id/': "Removed by owner",
}

# this list will be auto-generated
crawler_list = {}

# auto-import all submodules in the current directory
__module_regex = re.compile(r'^([^_.][^.]+).py[c]?$', re.I)
__url_regex = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)

for entry in os.listdir(__path__[0]):
    file_path = os.path.join(__path__[0], entry)
    if not os.path.isfile(file_path):
        continue
    # end if

    regex_result = __module_regex.findall(entry)
    if len(regex_result) != 1:  # does not contains a module
        continue
    # end if

    module_name = regex_result[0]
    module = importlib.import_module('.' + module_name, package=__package__)

    for key in dir(module):
        item = getattr(module, key)
        if type(item) != type(Crawler) or item.__base__ != Crawler:
            continue
        # end if

        if not hasattr(item, 'base_url'):
            raise Exception('No `base_url` for `%s`' % key)
        # end if

        base_url = getattr(item, 'base_url')
        if isinstance(base_url, str):
            base_url = [base_url]
        # end if

        if not isinstance(base_url, list):
            raise Exception('Unexpected `base_url` type in `%s`' % key)
        # end if

        for url in base_url:
            if not __url_regex.match(url):
                raise Exception('Invalid `base_url` in `%s`: %s' % (key, url))
            # end if
            if not url.endswith('/'):
                url += '/'
            # end if
            if url in rejected_sources:
                continue
            # end if
            crawler_list[url] = item
        # end for
    # end for
# end for
