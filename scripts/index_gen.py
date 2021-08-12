#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build lightnovel-crawler source index to use for update checking.
"""
import hashlib
import json
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Event
from typing import Dict
from urllib.parse import quote_plus

import cloudscraper

WORKDIR = Path(__file__).parent.parent.absolute()

SOURCES_FOLDER = WORKDIR / 'sources'
INDEX_FILE = SOURCES_FOLDER / '_index.json'
REJECTED_FILE = SOURCES_FOLDER / '_rejected.json'

README_FILE = WORKDIR / 'README.md'
SUPPORTED_SOURCE_LIST_QUE = '<!-- auto generated supported sources list -->'
REJECTED_SOURCE_LIST_QUE = '<!-- auto generated rejected sources list -->'

DATE_FORMAT = '%d %B %Y %I:%M:%S %p'

INDEX_DATA = {
    'v': int(time.time()),
    'app': {
        'windows': 'https://rebrand.ly/lncrawl',
        'linux': 'https://rebrand.ly/lncrawl-linux',
    },
    'rejected': {},
    'supported': {},
    'crawlers': {},
}

executor = ThreadPoolExecutor(8)
session = cloudscraper.create_scraper()

# =========================================================================================== #
# The index data
# =========================================================================================== #

print('-' * 50)
res = session.get('https://pypi.org/pypi/lightnovel-crawler/json')
res.raise_for_status()
pypi_data = res.json()
print('Latest version:', pypi_data['info']['version'])

INDEX_DATA['app']['version'] = pypi_data['info']['version']
INDEX_DATA['app']['home'] = pypi_data['info']['home_page']
INDEX_DATA['app']['pypi'] = pypi_data['info']['release_url']
print('-' * 50)

# =========================================================================================== #
# Generate sources index
# =========================================================================================== #

SOURCE_URL_PREFIX = 'https://github.com/dipu-bd/lightnovel-crawler/master/%s'
HISTORY_URL_PREFIX = 'https://github.com/dipu-bd/lightnovel-crawler/commits/master/%s'
SOURCE_DOWNLOAD_URL_PREFIX = 'https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/%s'
WHEEL_RELEASE_URL = 'https://github.com/dipu-bd/lightnovel-crawler/releases/download/v%s/lightnovel_crawler-%s-py3-none-any.whl'

queue_cache_result: Dict[str, str] = {}
queue_cache_event: Dict[str, Event] = {}

try:
    sys.path.insert(0, str(WORKDIR))
    from lncrawl.core.sources import __import_crawlers
except ImportError:
    traceback.print_exc()
    exit(1)

assert SOURCES_FOLDER.is_dir()

with open(REJECTED_FILE, encoding='utf8') as fp:
    rejected_sources = json.load(fp)

print('Getting contributors...')
res = session.get('https://api.github.com/repos/dipu-bd/lightnovel-crawler/contributors')
res.raise_for_status()
repo_contribs = {x['login']: x for x in res.json()}
print('Contributors:', ', '.join(repo_contribs.keys()))
print('-' * 50)


def search_user_by(query):
    if query in queue_cache_event:
        queue_cache_event[query].wait()
        return queue_cache_result[query]

    queue_cache_event[query] = Event()
    for _ in range(2):
        res = session.get('https://api.github.com/search/users?q=%s' % query)
        if res.status_code != 200:
            current_limit = int(res.headers.get('X-RateLimit-Remaining') or '0')
            if current_limit == 0:
                reset_time = int(time.time()) - int(res.headers.get('X-RateLimit-Reset') or '0')
                print(query, ':', 'Waiting %d seconds for reset...' % reset_time)
                time.sleep(reset_time + 2)
            continue
        data = res.json()
        for item in data['items']:
            if item['login'] in repo_contribs:
                queue_cache_result[query] = item['login']
                break
        break
    queue_cache_event[query].set()
    return queue_cache_result.get(query)


def git_history(file_path):
    try:
        cmd = 'git log --follow --diff-filter=AMT --pretty="%%at||%%aN||%%aE||%%s" "%s"' % file_path
        # cmd = 'git log -1 --diff-filter=AMT --pretty="%%at||%%aN||%%aE||%%s" "%s"' % file_path
        logs = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        logs = [line.strip().split('||', maxsplit=4) for line in logs.splitlines(False)]
        logs = [{'time': int(x[0]), 'author': x[1], 'email': x[2], 'subject': x[3]} for x in logs]
        return logs
    except Exception:
        traceback.print_exc()
        return {}

def process_contributors(history):
    contribs = set([])
    for data in history:
        author = data['author']
        email = data['email']
        if author in repo_contribs:
            contribs.add(author)
            continue
        name = search_user_by(quote_plus('%s in:email' % email))
        if name in repo_contribs:
            contribs.add(name)
            continue
        name = search_user_by(quote_plus('%s in:name' % author))
        if name in repo_contribs:
            contribs.add(name)
            continue
        #contribs.add(author)
    return list(contribs)

def process_file(py_file: Path) -> float:
    if not py_file.name[0].isalnum():
        return 0

    start = time.time()
    relative_path = py_file.relative_to(WORKDIR).as_posix()
    download_url = SOURCE_DOWNLOAD_URL_PREFIX % relative_path

    history = git_history(relative_path)

    with open(py_file, 'rb') as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    for crawler in __import_crawlers(py_file):
        can_login = 'login' in crawler.__dict__
        can_logout = 'logout' in crawler.__dict__
        can_search = 'search_novel' in crawler.__dict__
        source_id = hashlib.md5(str(crawler).encode('utf8')).hexdigest()

        info = {}
        info['id'] = source_id
        info['md5'] = md5
        info['url'] = download_url
        # info['name'] = crawler.__name__
        # info['filename'] = py_file.name
        info['version'] = history[0]['time']
        info['total_commits'] = len(history)
        info['file_path'] = str(relative_path)
        # info['last_commit'] = history[0]
        # info['first_commit'] = history[-1]
        # info['author'] = history[-1]['author']
        info['can_search'] = can_search
        info['can_login'] = can_login
        info['can_logout'] = can_logout
        info['base_urls'] = getattr(crawler, 'base_url')
        info['contributors'] = process_contributors(history)

        INDEX_DATA['crawlers'][source_id] = info
        for url in info['base_urls']:
            if url in rejected_sources:
                INDEX_DATA['rejected'][url] = rejected_sources[url]
            else:
                INDEX_DATA['supported'][url] = source_id

    return time.time() - start


futures = {}
for py_file in sorted(SOURCES_FOLDER.glob('**/*.py')):
    futures[py_file] = executor.submit(process_file, py_file)
for py_file, future in futures.items():
    print('> %-40s' % py_file.name, end='')
    runtime = future.result()
    print('%.3fs' % runtime)

print('-' * 50)
print('%d crawlers.' % len(INDEX_DATA['crawlers']),
      '%d supported urls.' % len(INDEX_DATA['supported']),
      '%d rejected urls.' % len(INDEX_DATA['rejected']))
print('-' * 50)

with open(INDEX_FILE, 'w', encoding='utf8') as fp:
    json.dump(INDEX_DATA, fp)  # , indent='  ')

# =========================================================================================== #
# Update README.md
# =========================================================================================== #

print('Rendering supported and rejected source list for README.md...')

with open(README_FILE, encoding='utf8') as fp:
    readme_text = fp.read()

before, supported, after = readme_text.split(SUPPORTED_SOURCE_LIST_QUE)
supported = '\n\n<table>\n<tbody>\n'
supported += '<tr>'
supported += '<th></th>\n'
supported += '<th>Source URL</th>\n'
supported += '<th>Version</th>\n'
# supported += '<th>Created At</th>\n'
supported += '<th>Contributors</th>\n'
supported += '</tr>\n'
for url, crawler_id in sorted(INDEX_DATA['supported'].items(), key=lambda x: x[0]):
    info = INDEX_DATA['crawlers'][crawler_id]
    source_url = SOURCE_URL_PREFIX % info['file_path']
    # history_url = HISTORY_URL_PREFIX % info['file_path']
    # created_at = datetime.fromtimestamp(info['first_commit']['time']).strftime(DATE_FORMAT)

    supported += '<tr>'
    supported += '<td>'
    supported += '<span title="Supports searching">%s</span>' % ('🔍' if info['can_search'] else '')
    supported += '<span title="Supports login">%s</span>' % ('🔑' if info['can_login'] else '')
    supported += '</td>\n'
    supported += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
    supported += '<td><a href="%s">%s</a></td>\n' % (source_url, info['version'])
    # supported += '<td><a href="%s">%s</a></td>\n' % (history_url, created_at)
    supported += '<td>%s</td>\n' % ' '.join([
        '<a href="%s" target="_blank"><img src="%s&s=24" alt="%s" height="24"/></a>' % (c['html_url'], c['avatar_url'], c['login'])
        for c in sorted([repo_contribs[x] for x in info['contributors']], key=lambda x: -x['contributions'])
    ])
    supported += '</tr>\n'
supported += '</tbody>\n</table>\n\n'
readme_text = SUPPORTED_SOURCE_LIST_QUE.join([before, supported, after])

print('Generated supported sources list.')

before, rejected, after = readme_text.split(REJECTED_SOURCE_LIST_QUE)
rejected = '\n\n<table>\n<tbody>\n'
rejected += '<tr>'
rejected += '<th>Source URL</th>\n'
rejected += '<th>Rejection Cause</th>\n'
rejected += '</tr>\n'
for url, cause in sorted(INDEX_DATA['rejected'].items(),  key=lambda x: x[0]):
    rejected += '<tr>'
    rejected += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
    rejected += '<td>%s</td>\n' % cause
    rejected += '</tr>\n'
rejected += '</tbody>\n</table>\n\n'
readme_text = REJECTED_SOURCE_LIST_QUE.join([before, rejected, after])

print('Generated rejected sources list.')

with open(README_FILE, 'w', encoding='utf8') as fp:
    fp.write(readme_text)

print('-' * 50)

executor.shutdown()
