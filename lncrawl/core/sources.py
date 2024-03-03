import hashlib
import importlib.util
import json
import logging
import os
import re
import time
from concurrent.futures import Future
from pathlib import Path
from typing import Dict, List, Optional, Set, Type
from urllib.parse import urlparse

import requests
from packaging import version

from ..assets.version import get_version
from ..assets.languages import language_codes
from ..utils.platforms import Platform
from .arguments import get_args
from .crawler import Crawler
from .display import new_version_news
from .exeptions import LNException
from .taskman import TaskManager

logger = logging.getLogger(__name__)

# --------------------------------------------------------------------------- #

__all__ = [
    "load_sources",
    "crawler_list",
    "rejected_sources",
]

rejected_sources = {}
template_list: Set[Type[Crawler]] = set()
crawler_list: Dict[str, Type[Crawler]] = {}

# --------------------------------------------------------------------------- #
# Utilities
# --------------------------------------------------------------------------- #

__executor = TaskManager()


def __download_data(url: str):
    logger.debug("Downloading %s", url)

    if Platform.windows:
        referer = "http://updater.checker/windows/" + get_version()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    elif Platform.linux:
        referer = "http://updater.checker/linux/" + get_version()
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    elif Platform.mac:
        referer = "http://updater.checker/mac/" + get_version()
        user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    elif Platform.java:
        referer = "http://updater.checker/java/" + get_version()
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0"
    else:
        referer = "http://updater.checker/others/" + get_version()
        user_agent = f"lncrawl/{get_version()} ({Platform.name})"

    res = requests.get(
        url,
        stream=True,
        allow_redirects=True,
        headers={
            "referer": referer,
            "user-agent": user_agent,
        },
    )

    res.raise_for_status()
    return res.content


# --------------------------------------------------------------------------- #
# Checking Updates
# --------------------------------------------------------------------------- #

__index_fetch_internval_in_seconds = 30 * 60
__master_index_file_url = "https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/sources/_index.json"

__user_data_path = Path("~").expanduser() / ".lncrawl"
__local_data_path = Path(__file__).parent.parent.absolute()
if not (__local_data_path / "sources").is_dir():
    __local_data_path = __local_data_path.parent

__current_index = {}
__latest_index = {}


def __load_current_index():
    try:
        index_file = __user_data_path / "sources" / "_index.json"
        if not index_file.is_file():
            index_file = __local_data_path / "sources" / "_index.json"

        assert index_file.is_file(), "Invalid index file"

        logger.debug("Loading current index data from %s", index_file)
        with open(index_file, "r", encoding="utf8") as fp:
            global __current_index
            __current_index = json.load(fp)
    except Exception as e:
        logger.debug("Could not load sources index. Error: %s", e)


def __save_current_index():
    index_file = __user_data_path / "sources" / "_index.json"
    index_file.parent.mkdir(parents=True, exist_ok=True)

    logger.debug("Saving current index data to %s", index_file)
    with open(index_file, "w", encoding="utf8") as fp:
        json.dump(__current_index, fp, ensure_ascii=False)


def __load_latest_index():
    global __latest_index
    global __current_index

    last_download = __current_index.get("v", 0)
    if time.time() - last_download < __index_fetch_internval_in_seconds:
        logger.debug("Current index was already downloaded once")
        __latest_index = __current_index
        return

    try:
        data = __download_data(__master_index_file_url)
        __latest_index = json.loads(data.decode("utf8"))
        if "crawlers" not in __current_index:
            __current_index = __latest_index
        __current_index["v"] = int(time.time())
        __save_current_index()
    except Exception as e:
        if "crawlers" not in __current_index:
            raise LNException("Could not fetch sources index")
        logger.warning("Could not download latest index. Error: %s", e)
        __latest_index = __current_index


def __check_updates():
    __load_current_index()
    __load_latest_index()

    latest_app_version = __latest_index["app"]["version"]
    if version.parse(latest_app_version) > version.parse(get_version()):
        new_version_news(latest_app_version)

    global __current_index
    __current_index["app"] = __latest_index["app"]
    __current_index["supported"] = __latest_index["supported"]
    __current_index["rejected"] = __latest_index["rejected"]
    __save_current_index()

    global rejected_sources
    rejected_sources = __current_index["rejected"]


# --------------------------------------------------------------------------- #
# Downloading sources
# --------------------------------------------------------------------------- #


def __save_source_data(source_id, data):
    latest = __latest_index["crawlers"][source_id]
    dst_file = __user_data_path / str(latest["file_path"])
    dst_dir = dst_file.parent
    temp_file = dst_dir / ("." + dst_file.name)

    dst_dir.mkdir(parents=True, exist_ok=True)
    with open(temp_file, "wb") as fp:
        fp.write(data)

    if dst_file.exists():
        dst_file.unlink()
    temp_file.rename(dst_file)

    global __current_index
    __current_index["crawlers"][source_id] = latest
    __save_current_index()

    logger.debug("Source update downloaded: %s", dst_file.name)


# def __get_file_md5(file: Path):
#     if not file.is_file():
#         return None
#     with open(file, "rb") as f:
#         return hashlib.md5(f.read()).hexdigest()


def __download_sources():
    tbd_sids = []
    for sid in __current_index["crawlers"].keys():
        if sid not in __latest_index["crawlers"]:
            tbd_sids.append(sid)
    for sid in tbd_sids:
        del __current_index["crawlers"][sid]

    futures: Dict[str, Future] = {}
    for sid, latest in __latest_index["crawlers"].items():
        current = __current_index["crawlers"].get(sid)
        has_new_version = not current or current["version"] < latest["version"]
        __current_index["crawlers"][sid] = latest
        user_file = (__user_data_path / str(latest["file_path"])).is_file()
        local_file = (__local_data_path / str(latest["file_path"])).is_file()
        if has_new_version or not (user_file or local_file):
            future = __executor.submit_task(__download_data, latest["url"])
            futures[sid] = future

    if not futures:
        return

    __executor.resolve_futures(futures.values(), desc="Sources", unit="file")
    for sid, future in futures.items():
        try:
            data = future.result()
        except Exception:
            continue
        try:
            __save_source_data(sid, data)
        except Exception as e:
            logger.warning("Failed to save source file. Error: %s", e)


# --------------------------------------------------------------------------- #
# Loading sources
# --------------------------------------------------------------------------- #

__cache_crawlers = {}
__url_regex = re.compile(r"^^(https?|ftp)://[^\s/$.?#].[^\s]*$", re.I)


def __import_crawlers(file_path: Path) -> List[Type[Crawler]]:
    global __cache_crawlers
    if file_path in __cache_crawlers:
        return __cache_crawlers[file_path]

    # logger.debug('+ %s', file_path)
    assert file_path.is_file(), "Invalid crawler file path"

    try:
        module_name = hashlib.md5(file_path.name.encode()).hexdigest()
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
    except Exception as e:
        logger.warning("Module load failed: %s | %s", file_path, e)
        return []

    language_code = ""
    for part in reversed(file_path.parts):
        if part in language_codes:
            language_code = part
            break

    crawlers = []
    for key in dir(module):
        crawler = getattr(module, key)
        if type(crawler) is not type(Crawler) or not issubclass(crawler, Crawler):
            continue

        if crawler.__dict__.get("is_template"):
            template_list.add(crawler)
            continue

        urls = getattr(crawler, "base_url", [])
        urls = [urls] if isinstance(urls, str) else list(urls)
        urls = list(set([str(url).lower().strip("/") + "/" for url in urls]))
        if not urls:
            continue
        for url in urls:
            assert __url_regex.match(url), f"Invalid base url: {url} @{file_path}"

        for method in ["read_novel_info", "download_chapter_body"]:
            if not hasattr(crawler, method):
                raise LNException(f"Required method not found: {method} @{file_path}")
            if not callable(getattr(crawler, method)):
                raise LNException(f"Should be callable: {method} @{file_path}")

        setattr(crawler, "base_url", urls)
        setattr(crawler, "language", language_code)
        setattr(crawler, "file_path", str(file_path.absolute()))

        crawlers.append(crawler)

    __cache_crawlers[file_path] = crawlers
    return crawlers


def __add_crawlers_from_path(path: Path):
    if path.name.startswith("_") or not path.name[0].isalnum():
        return

    if not path.exists():
        logger.warning("Path does not exists: %s", path)
        return

    if path.is_dir():
        for py_file in path.glob("**/*.py"):
            __add_crawlers_from_path(py_file)
        return

    global crawler_list
    try:
        crawlers = __import_crawlers(path)
        for crawler in crawlers:
            setattr(crawler, "file_path", str(path.absolute()))
            for url in getattr(crawler, "base_url"):
                crawler_list[url] = crawler
    except Exception as e:
        logger.warning("Could not load crawlers from %s. Error: %s", path, e)


# --------------------------------------------------------------------------- #
# Public methods
# --------------------------------------------------------------------------- #

sources_path = (__local_data_path / "sources").absolute()


def load_sources():
    __is_dev_mode = (
        os.getenv("LNCRAWL_MODE") == "dev"
        or (__local_data_path / ".git" / "HEAD").exists()
    )

    if not __is_dev_mode:
        __check_updates()
        __download_sources()
        __save_current_index()

    __add_crawlers_from_path(__local_data_path / "sources")

    if not __is_dev_mode:
        for _, current in __current_index["crawlers"].items():
            source_file = __user_data_path / str(current["file_path"])
            if source_file.is_file():
                __add_crawlers_from_path(source_file)

    args = get_args()
    for crawler_file in args.crawler:
        __add_crawlers_from_path(Path(crawler_file))


def prepare_crawler(url: str) -> Optional[Crawler]:
    if not url:
        return None

    parsed_url = urlparse(url)
    base_url = "%s://%s/" % (parsed_url.scheme, parsed_url.hostname)
    if base_url in rejected_sources:
        raise LNException("Source is rejected. Reason: " + rejected_sources[base_url])

    CrawlerType = crawler_list.get(base_url)
    if not CrawlerType:
        raise LNException("No crawler found for " + base_url)

    logger.info(
        "Initializing crawler for: %s [%s]",
        base_url,
        getattr(CrawlerType, "file_path", "."),
    )
    crawler = CrawlerType()
    crawler.home_url = base_url
    crawler.novel_url = url
    crawler.initialize()
    return crawler
