# -*- coding: utf-8 -*-
import hashlib
import importlib.util
import json
import logging
import os
import re
import time
from concurrent.futures import Future, ThreadPoolExecutor
from importlib.abc import FileLoader
from pathlib import Path
from typing import Dict, List, Type

import requests
from packaging import version
from tqdm.std import tqdm

from ..assets.icons import Icons
from ..assets.version import get_value
from .arguments import get_args
from .crawler import Crawler
from .display import new_version_news

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #

__all__ = [
    'load_sources',
    'crawler_list',
    'rejected_sources',
]

rejected_sources = {}
crawler_list: Dict[str, Type[Crawler]] = {}

# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #

__executor = ThreadPoolExecutor(10)


def __download_data(url: str):
    logger.debug('Downloading %s', url)

    if Icons.isWindows:
        referer = 'http://updater.checker/windows/' + get_value()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    elif Icons.isLinux:
        referer = 'http://updater.checker/linux/' + get_value()
        user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    elif Icons.isMac:
        referer = 'http://updater.checker/mac/' + get_value()
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
    else:
        referer = 'http://updater.checker/others/' + get_value()
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0'
    # end if

    res = requests.get(
        url,
        stream=True,
        allow_redirects=True,
        headers={
            'referer': referer,
            'user-agent': user_agent,
        }
    )

    res.raise_for_status()
    return res.content


# --------------------------------------------------------------------------- #
# Checking Updates
# --------------------------------------------------------------------------- #

__index_fetch_internval_in_hours = 3
__master_index_file_url = 'https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/_index.json'

__user_data_path = Path(os.path.expanduser('~')) / '.lncrawl'
__local_data_path = Path(__file__).parent.parent.absolute()
if not (__local_data_path / 'sources').is_dir():
    __local_data_path = __local_data_path.parent

__current_index_data = {}
__latest_index_data = {}

__is_dev_mode = (__local_data_path / '.git' / 'HEAD').exists()


def __load_current_index_data():
    index_file = __user_data_path / 'sources' / '_index.json'
    if not index_file.is_file():
        index_file = __local_data_path / 'sources' / '_index.json'

    assert index_file.is_file()

    logger.debug('Loading current index data from %s', index_file)
    with open(index_file, 'r', encoding='utf8') as fp:
        global __current_index_data
        __current_index_data = json.load(fp)


def __save_current_index_data():
    if __is_dev_mode:
        return

    index_file = __user_data_path / 'sources' / '_index.json'
    os.makedirs(index_file.parent, exist_ok=True)

    logger.debug('Saving current index data to %s', index_file)
    with open(index_file, 'w', encoding='utf8') as fp:
        json.dump(__current_index_data, fp, ensure_ascii=False)


def __load_latest_index_data():
    global __latest_index_data
    global __current_index_data

    if __is_dev_mode:
        __latest_index_data = __current_index_data

    last_download = __current_index_data.get('last_download', 0)
    if time.time() - last_download < __index_fetch_internval_in_hours * 3600:
        logger.debug('Current index was already downloaded once in last %d hours.',
                     __index_fetch_internval_in_hours)
        __latest_index_data = __current_index_data
        return

    try:
        data = __download_data(__master_index_file_url)
        __latest_index_data = json.loads(data.decode('utf8'))
        __current_index_data['last_download'] = time.time()
        __save_current_index_data()
    except Exception as e:
        logger.warn('Could not download latest index. Error: %s', e)
        __latest_index_data = __current_index_data


def __check_updates():
    __load_current_index_data()
    __load_latest_index_data()

    latest_app_version = __latest_index_data['app']['version']
    if version.parse(latest_app_version) > version.parse(get_value()):
        new_version_news(latest_app_version)

    global __current_index_data
    __current_index_data['app'] = __latest_index_data['app']
    __save_current_index_data()

    global rejected_sources
    rejected_sources = __latest_index_data['rejected']


# --------------------------------------------------------------------------- #
# Downloading sources
# --------------------------------------------------------------------------- #

def __save_source_data(source_id, data):
    latest = __latest_index_data['crawlers'][source_id]
    dst_file = __user_data_path / str(latest['file_path'])
    dst_dir = dst_file.parent
    temp_file = dst_dir / ('.' + dst_file.name)

    os.makedirs(dst_dir, exist_ok=True)
    with open(temp_file, 'wb') as fp:
        fp.write(data)

    if dst_file.exists():
        os.remove(dst_file)
    temp_file.rename(dst_file)

    global __current_index_data
    __current_index_data['crawlers'][source_id] = latest
    __save_current_index_data()

    logger.debug('Source update downloaded: %s', dst_file.name)


def __get_file_md5(file: Path):
    if not file.is_file():
        return None
    with open(file, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()


def __download_sources():
    if __is_dev_mode:
        return

    futures: Dict[str, Future] = {}
    for sid, latest in __latest_index_data['crawlers'].items():
        current = __current_index_data['crawlers'].get(sid)
        has_new_version = not current or current['version'] < latest['version']
        user_file = (__user_data_path / str(latest['file_path'])).is_file()
        local_file = (__local_data_path / str(latest['file_path'])).is_file()
        if has_new_version or not (user_file or local_file):
            future = __executor.submit(__download_data, latest['url'])
            futures[sid] = future

    if not futures:
        return

    bar = tqdm(desc='Updating sources', total=len(futures), unit='file')
    if os.getenv('debug_mode') == 'yes':
        bar.update = lambda n=1: None  # Hide in debug mode
    bar.clear()

    for sid, future in futures.items():
        try:
            data = future.result()
            __save_source_data(sid, data)
        except Exception as e:
            logger.warn('Failed to download source file. Error: %s', e)
        finally:
            bar.update()

    bar.clear()
    bar.close()

# --------------------------------------------------------------------------- #
# Loading sources
# --------------------------------------------------------------------------- #


__cache_crawlers = {}
__url_regex = re.compile(r'^^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)


def __import_crawlers(file_path: Path) -> List[Type[Crawler]]:
    global __cache_crawlers
    if file_path in __cache_crawlers:
        return __cache_crawlers[file_path]

    # logger.debug('+ %s', file_path)
    assert file_path.is_file()

    module_name = hashlib.md5(file_path.name.encode()).hexdigest()
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    assert spec and isinstance(spec.loader, FileLoader)

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

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

        setattr(crawler, 'base_url', urls)
        crawlers.append(crawler)
    # end for

    __cache_crawlers[file_path] = crawlers
    return crawlers
# end def


def __add_crawlers_from_path(path: Path):
    if not path.exists():
        logger.warn('Path does not exists: %s', path)
        return

    if path.is_dir():
        for py_file in path.glob('**/*.py'):
            __add_crawlers_from_path(py_file)
        return

    global crawler_list
    try:
        crawlers = __import_crawlers(path)
        for crawler in crawlers:
            for url in getattr(crawler, 'base_url'):
                crawler_list[url] = crawler
    except Exception as e:
        logger.warn('Could not load crawlers from %s. Error: %s', path, e)


def __load_all_sources():
    __add_crawlers_from_path(__local_data_path / 'sources')

    for _, current in __current_index_data['crawlers'].items():
        source_file = __user_data_path / str(current['file_path'])
        if source_file.is_file():
            __add_crawlers_from_path(source_file)

    args = get_args()
    for crawler_file in args.crawler:
        __add_crawlers_from_path(Path(crawler_file))


def load_sources():
    __check_updates()
    __download_sources()
    __load_all_sources()
    __save_current_index_data()
