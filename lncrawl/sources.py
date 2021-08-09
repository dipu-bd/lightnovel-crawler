# -*- coding: utf-8 -*-
import hashlib
import importlib.util
import logging
import re
from importlib.abc import FileLoader
from pathlib import Path
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)

rejected_sources = {}
crawler_list: Dict[str, Callable[[], Any]] = {}

__url_regex = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)


def __import_module(file_path):
    file_path = Path(file_path)
    assert file_path.is_file()

    module_name = hashlib.md5(file_path.name.encode()).hexdigest()
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    assert spec and isinstance(spec.loader, FileLoader)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module


def load_crawlers(file_path):
    from .core.crawler import Crawler

    module = __import_module(file_path)

    crawlers = []
    for key in dir(module):
        crawler = getattr(module, key)
        if type(crawler) != type(Crawler) or crawler.__base__ != Crawler:
            continue

        assert 'base_url' in crawler.__dict__
        assert 'read_novel_info' in crawler.__dict__
        assert 'download_chapter_body' in crawler.__dict__

        urls = getattr(crawler, 'base_url')
        if isinstance(urls, str):
            urls = [urls]

        assert isinstance(urls, list)

        urls = [
            str(url).lower().strip('/') + '/'
            for url in set(urls)
        ]
        assert len(urls) > 0

        for url in urls:
            assert __url_regex.match(url)

        can_login = 'login' in crawler.__dict__
        can_logout = 'logout' in crawler.__dict__
        can_search = 'search_novel' in crawler.__dict__

        crawlers.append({
            'name': crawler.__name__,
            'filename': file_path.name,
            'can_search': can_search,
            'can_login': can_login,
            'can_logout': can_logout,
            'base_urls': urls,
        })
    # end for

    return crawlers
# end def


def add_rejected(url: str, cause: str):
    global rejected_sources
    rejected_sources[url] = cause
    if url in crawler_list:
        del crawler_list[url]
    # end if
# end def


def add_crawler(file_path, crawler_info: dict):
    global crawler_list

    module = __import_module(file_path)
    crawler = getattr(module, crawler_info['name'])
    assert crawler

    for url in crawler_info['base_urls']:
        if url not in rejected_sources:
            crawler_list[url] = crawler
        # end if
    # end for
# end def


def add_all_crawlers(file_path: str):
    for crawler_info in load_crawlers(file_path):
        add_crawler(file_path, crawler_info)
    # end for
# end def
