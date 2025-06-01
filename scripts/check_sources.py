#!/usr/bin/env python3
"""
Finds dead sources, and adds them to rejected list automatically
"""
import sys
from concurrent.futures import Future
from pathlib import Path

import cloudscraper  # type:ignore
from colorama import Fore, Style
from requests import Response
from requests.exceptions import (ConnectionError, InvalidHeader, Timeout,
                                 TooManyRedirects)
from urllib3 import disable_warnings

workdir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(workdir))

try:
    from lncrawl.assets.chars import Chars
    from lncrawl.assets.user_agents import user_agents
    from lncrawl.core.sources import crawler_list, load_sources
    from lncrawl.core.taskman import TaskManager
except ImportError:
    raise


def main():
    # Setup
    disable_warnings()
    taskman = TaskManager(20)
    session = cloudscraper.create_scraper()

    # Load all urls
    load_sources()
    rejected_json = {}
    urls_to_check = set()
    for CrawlerType in crawler_list.values():
        for url in CrawlerType.base_url:
            if CrawlerType.is_disabled:
                rejected_json[url] = CrawlerType.disable_reason or 'Disabled'
            else:
                urls_to_check.add(url)

    # Create futures
    futures = {}
    for i, url in enumerate(sorted(urls_to_check)):
        futures[url] = taskman.submit_task(
            session.get, url, timeout=5, stream=True,
            headers={
                'User-Agent': user_agents[i % len(user_agents)],
            }
        )

    # Resolve futures
    total = len(urls_to_check)
    for i, (url, f) in enumerate(futures.items()):
        print(f'{Style.DIM}{Fore.CYAN}{i + 1:03}/{total:03}{Style.RESET_ALL}', end=' ')
        print(f'{Style.BRIGHT}{url}{Style.RESET_ALL}', end=f' {Chars.RIGHT_ARROW} ')
        try:
            assert isinstance(f, Future)
            response: Response = f.result()
            message = f'{response.status_code} {response.reason}'
            is_cloudflare = response.headers.get('Server') != 'cloudflare'
            print(f'{Style.DIM}{message}{Style.RESET_ALL}', end=' ')
            if is_cloudflare:
                print(f"{Fore.GREEN}[cloudflare]{Fore.RESET}", end='')
            if response.status_code >= 400 and not is_cloudflare:
                rejected_json[url] = message
            elif url in rejected_json:
                del rejected_json[url]
            print()
        except (ConnectionError, Timeout, TooManyRedirects, InvalidHeader) as e:
            rejected_json[url] = 'Site is down'
            print(f'{Style.DIM}{Fore.BLUE}{repr(e)}{Style.RESET_ALL}')
        except Exception as e:
            print(f'{Fore.RED}{repr(e)}{Fore.RESET}')

    return dict(sorted(rejected_json.items()))


if __name__ == '__main__':
    result = main()
    print('-' * 40)
    print(main())
