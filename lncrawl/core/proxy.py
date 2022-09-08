import atexit
import logging
import random
from typing import Dict, List
import signal
import time
from threading import Thread

from bs4 import BeautifulSoup
from requests import RequestException, Session

from ..assets.user_agents import user_agents
from ..utils.ssl_no_verify import no_ssl_verification

logger = logging.getLogger(__name__)

__has_exit = False
__proxy_ttl = 3600
__max_use_per_proxy = 50

__sess = Session()
__proxy_list: Dict[str, List[str]] = {}
__proxy_visited_at: Dict[str, int] = {}
__proxy_use_count: Dict[str, int] = {}
__circular_index: Dict[str, int] = {}


def get_a_proxy(scheme: str = 'http', timeout: int = 0):
    if timeout > 0:
        wait_for_first_proxy(scheme, timeout)
    # end if
    if scheme not in __proxy_list:
        return
    # end if

    proxy_list = [
        url
        for url in __proxy_list[scheme]
        if __proxy_visited_at[url] + __proxy_ttl > time.time()
            and __proxy_use_count.get(url, 0) < __max_use_per_proxy
    ]
    __proxy_list[scheme] = proxy_list
    if len(proxy_list) == 0:
        return
    # end if

    __circular_index.setdefault(scheme, -1)
    __circular_index[scheme] += 1
    __circular_index[scheme] %= len(proxy_list)

    url = proxy_list[__circular_index[scheme]]
    __proxy_use_count[url] = __proxy_use_count.get(url, 0) + 1
    return url
# end def


def remove_faulty_proxies(faulty_url: str):
    if faulty_url:
        __proxy_use_count[faulty_url] = __max_use_per_proxy + 1
    # end if
# end def


def wait_for_first_proxy(scheme: str, timeout: int = 0):
    if timeout <= 0:
        timeout = 10 * 60
    # end if
    elapsed = 0
    while not __has_exit and elapsed < timeout:
        for k, v in __proxy_list.items():
            if v and (not scheme or k == scheme):
                return True
        time.sleep(0.1)
        elapsed += 0.1
    # end while
# end def


def __validate_and_add(scheme: str, ip: str, url: str):
    try:
        if __proxy_use_count.get(url, 0) >= __max_use_per_proxy:
            return
        # end if
        with no_ssl_verification():
            resp = __sess.get(
                f'{scheme}://api.ipify.org/', 
                proxies={ scheme: url },
                allow_redirects=True,
                timeout=3,
            )
            resp.raise_for_status()
        if resp.text.strip() == ip:
            # print('>>>>>> found', url)
            __proxy_list[scheme].append(url)
            return True
        # end if
    except RequestException as e:
        # print(url, e)
        pass
    # end try
# end def


def __get_free_proxy_list(url):
    with no_ssl_verification():
        resp = __sess.get(
            url,
            headers={'user-agent': user_agents[0]},
            timeout=5
        )
    if resp.status_code >= 400:
        return []
    # end if
    html = resp.content.decode('utf8', 'ignore')
    soup = BeautifulSoup(html, 'lxml')
    return [
        [td.text for td in tr.select('td')]
        for tr in soup.select('.fpl-list table tbody tr')
    ]
# end def


def __find_proxies():
    err_count = 0
    while err_count < 3 and not __has_exit:
        logger.debug('Fetching proxies | Current checklist: %d', len(__proxy_visited_at))
        try:
            rows = __get_free_proxy_list('https://free-proxy-list.net/')
            rows += __get_free_proxy_list('https://www.sslproxies.org/')
            random.shuffle(rows)
            err_count = 0

            for cols in rows:
                if __has_exit:
                    break
                if 'hour' in cols[7]:
                    continue
                if cols[4] not in ['anonymous', 'transparent']:
                    continue
                # end if
 
                ip = cols[0]
                port = cols[1]      
                scheme = 'https' if cols[6] == 'yes' else 'http'
                url = f'{scheme}://{ip}:{port}'

                __proxy_list.setdefault(scheme, [])
                if __proxy_visited_at.get(url, 0) + __proxy_ttl < time.time():
                    __validate_and_add(scheme, ip, url)
                    __proxy_visited_at[url] = time.time()

            wait_times = 3 * 60
            while wait_times and not __has_exit:
                time.sleep(1)
                wait_times -= 1
        except RequestException:
            err_count += 1
        except Exception as e:
            logger.debug('Failed to update proxy list', e)
            stop_proxy_fetcher()
        # end try
    # end while
# end def


def start_proxy_fetcher():
    atexit.register(stop_proxy_fetcher)
    signal.signal(signal.SIGINT, stop_proxy_fetcher)
    Thread(target=__find_proxies, daemon=False).start()
# end def


def stop_proxy_fetcher():
    global __has_exit
    __has_exit = True
# end def

