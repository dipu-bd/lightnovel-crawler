# -*- coding: utf-8 -*-

import hashlib
import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Optional

import requests
from packaging import version
from tqdm.std import tqdm

from ..assets.icons import Icons
from ..assets.version import get_value
from ..core.display import new_version_news
from ..sources import add_crawler, add_rejected

logger = logging.getLogger(__name__)

minimum_fetch_interval_in_seconds = 12 * 60 * 60

current_version = version.parse(get_value())
master_index_file_url = 'https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/_index.json'


def download_file(url: str, source_file: Path):
    logger.debug('Downloading file: %s from: %s', source_file, url)

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
    data = res.content

    source_dir = source_file.parent
    os.makedirs(source_dir, exist_ok=True)
    temp_file = source_dir / ('.' + source_file.name)
    with open(str(temp_file), 'wb') as f:
        f.write(data)
    # end with
    if source_file.exists():
        os.remove(source_file)
    temp_file.rename(source_file)

    return data
# end def


def update_sources(updates: dict):
    if not updates:
        return
    # end if

    bar = tqdm(desc='Update sources', total=len(updates), unit='file')
    if os.getenv('debug_mode') == 'yes':
        bar.update = lambda n=1: None  # Hide in debug mode
    # end if
    bar.clear()

    executor = ThreadPoolExecutor(10)
    futures = [
        executor.submit(download_file, url, file)
        for url, file in updates.items()
    ]
    for f in futures:
        try:
            f.result()
        except Exception as e:
            bar.clear()
            logger.error('Failed to download source. Cause: %s', e)
        finally:
            bar.update()
        # end try
    # end for
    bar.close()
    executor.shutdown()
# end def


def check_updates():
    source_data_path = Path(os.path.expanduser('~')) / '.lncrawl'
    user_index_file = source_data_path / 'sources' / '_index.json'
    dev_index_file = Path(__file__).parent.parent.parent.absolute() / 'sources' / '_index.json'

    need_to_fetch = True
    if dev_index_file.is_file():
        source_data_path = dev_index_file.parent.parent
        user_index_file = dev_index_file
        need_to_fetch = False
        logger.info('Using dev index: %s [fetch = %s]', dev_index_file, need_to_fetch)
    # end if

    user_data: Optional[dict] = None
    if user_index_file.is_file():
        logger.debug('Loading local index: %s', user_index_file)
        with open(user_index_file, 'r', encoding='utf8') as fp:
            user_data = json.load(fp)
        # end with
        if need_to_fetch:
            modify_age = time.time() - user_index_file.stat().st_mtime
            need_to_fetch = modify_age > minimum_fetch_interval_in_seconds
            logger.debug('Index file age: %.3f hours [fetch = %s]',
                         modify_age / 3660, need_to_fetch)
        # end if
    # end if

    latest_data: Optional[dict] = None
    if need_to_fetch:
        latest_data_bytes = download_file(master_index_file_url, user_index_file)
        latest_data = json.loads(latest_data_bytes.decode('utf8'))
    else:
        latest_data = user_data
    # end if

    if not latest_data:
        raise Exception('Index file was not found')
    # end if

    latest_version = str(latest_data['app']['version'])
    if current_version < version.parse(latest_version):
        new_version_news(latest_version)
    # end if

    for url, cause in latest_data['rejected'].items():
        add_rejected(url, cause)
    # end for

    source_updates = {}
    for info in latest_data['crawlers'].values():
        source_file = source_data_path / str(info['file_path'])

        source_md5 = None
        if source_file.is_file():
            with open(source_file, 'rb') as fp:
                source_md5 = hashlib.md5(fp.read()).hexdigest()

        if source_md5 != info['md5'] and user_index_file != dev_index_file:
            logger.debug('%s | %s (current) != %s (latest)', source_file, source_md5, info['md5'])
            source_updates[info['url']] = source_file
        # end if
    # end for

    update_sources(source_updates)

    for info in latest_data['crawlers'].values():
        source_file = source_data_path / str(info['file_path'])
        add_crawler(source_file, info)
    # end for
# end def
