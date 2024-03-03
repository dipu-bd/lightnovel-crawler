import atexit
import logging
import os
import random
import signal
import time
from threading import Thread
from typing import Dict, List

from bs4 import BeautifulSoup
from requests import RequestException, Session

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification

logger = logging.getLogger(__name__)

__has_exit = True
__proxy_ttl = 3600
__max_use_per_proxy = 50

__sess = Session()
__proxy_list: Dict[str, List[str]] = {}
__proxy_visited_at: Dict[str, int] = {}
__proxy_use_count: Dict[str, int] = {}
__circular_index: Dict[str, int] = {}
__is_private_proxy: Dict[str, bool] = {}


def load_proxies(proxy_file: str):
    with open(proxy_file, encoding="utf-8") as f:
        lines = f.read().splitlines()

    for line in set(lines):
        address = line.strip()
        if not address:
            continue
        if "://" in address:
            scheme, address = line.split("://")
            schemes = [scheme]
        else:
            schemes = ["http", "https"]

        for scheme in schemes:
            __proxy_list.setdefault(scheme, [])
            url = scheme + "://" + address
            __proxy_list[scheme].append(url)
            __is_private_proxy[url] = True


def get_a_proxy(scheme: str = "http", timeout: int = 0):
    if timeout > 0:
        wait_for_first_proxy(scheme, timeout)

    proxy_list = __proxy_list.get(scheme)
    if isinstance(proxy_list, list) and not __has_exit:
        proxy_list = [
            url
            for url in proxy_list
            if __proxy_visited_at[url] + __proxy_ttl > time.time()
            and __proxy_use_count.get(url, 0) < __max_use_per_proxy
        ]
        __proxy_list[scheme] = proxy_list

    if not proxy_list:
        return

    __circular_index.setdefault(scheme, -1)
    __circular_index[scheme] += 1
    __circular_index[scheme] %= len(proxy_list)

    url = proxy_list[__circular_index[scheme]]
    __proxy_use_count[url] = __proxy_use_count.get(url, 0) + 1
    return url


def remove_faulty_proxies(faulty_url: str):
    if faulty_url and not __is_private_proxy[faulty_url]:
        __proxy_use_count[faulty_url] = __max_use_per_proxy + 1


def wait_for_first_proxy(scheme: str, timeout: int = 0):
    if timeout <= 0:
        timeout = 10 * 60

    elapsed = 0
    while not __has_exit and elapsed < timeout:
        for k, v in __proxy_list.items():
            if v and (not scheme or k == scheme):
                return True
        time.sleep(0.1)
        elapsed += 0.1


def __validate_and_add(scheme: str, ip: str, url: str):
    try:
        if __proxy_use_count.get(url, 0) >= __max_use_per_proxy:
            return

        with no_ssl_verification():
            resp = __sess.get(
                f"{scheme}://api.ipify.org/",
                proxies={scheme: url},
                allow_redirects=True,
                timeout=3,
            )
            resp.raise_for_status()
        if resp.text.strip() == ip:
            # print('>>>>>> found', url)
            __proxy_list[scheme].append(url)
            return True
    except RequestException:
        # print(url, e)
        pass


def __get_free_proxy_list(url):
    with no_ssl_verification():
        resp = __sess.get(url, headers={"user-agent": user_agents[0]}, timeout=5)
    if resp.status_code >= 400:
        return []

    html = resp.content.decode("utf8", "ignore")
    soup = BeautifulSoup(html, "lxml")
    return [
        [td.text for td in tr.select("td")]
        for tr in soup.select(".fpl-list table tbody tr")
    ]


def __find_proxies():
    err_count = 0
    while err_count < 3 and not __has_exit:
        logger.debug(
            "Fetching proxies | Current checklist: %d", len(__proxy_visited_at)
        )
        try:
            rows = __get_free_proxy_list("https://free-proxy-list.net/")
            rows += __get_free_proxy_list("https://www.sslproxies.org/")
            random.shuffle(rows)
            err_count = 0

            for cols in rows:
                if __has_exit:
                    break
                if "hour" in cols[7]:
                    continue
                if cols[4] not in ["anonymous", "transparent"]:
                    continue

                ip = cols[0]
                port = cols[1]
                scheme = "https" if cols[6] == "yes" else "http"
                url = f"{scheme}://{ip}:{port}"

                __proxy_list.setdefault(scheme, [])
                if __proxy_visited_at.get(url, 0) + __proxy_ttl < time.time():
                    __validate_and_add(scheme, ip, url)
                    __proxy_visited_at[url] = int(time.time())

            wait_times = 3 * 60
            while wait_times and not __has_exit:
                time.sleep(1)
                wait_times -= 1
        except RequestException:
            err_count += 1
        except Exception as e:
            if os.getenv("debug_mode"):
                logger.error("Failed to update proxy list", e)
            stop_proxy_fetcher()


def start_proxy_fetcher():
    global __has_exit
    __has_exit = False
    atexit.register(stop_proxy_fetcher)
    signal.signal(signal.SIGINT, stop_proxy_fetcher)
    Thread(target=__find_proxies, daemon=False).start()


def stop_proxy_fetcher(*args, **kwargs):
    global __has_exit
    __has_exit = True
