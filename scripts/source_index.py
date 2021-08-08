#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build lightnovel-crawler source index to use for update checking.
"""
import hashlib
import importlib.util
import json
from datetime import datetime
import re
import subprocess
import traceback
from concurrent.futures import ThreadPoolExecutor
from importlib.abc import FileLoader
from pathlib import Path

from lncrawl.core.crawler import Crawler

SOURCE_DOWNLOAD_URL_PREFIX = 'https://raw.githubusercontent.com/dipu-bd/lightnovel-crawler/master/%s'

WORKDIR = Path(__file__).parent.parent.absolute()

SOURCES_FOLDER = WORKDIR / 'sources'
INDEX_FILE = SOURCES_FOLDER / '_index.json'
REJECTED_FILE = SOURCES_FOLDER / '_rejected.json'

README_FILE = WORKDIR / 'README.md'
SUPPORTED_SOURCE_LIST_QUE = '<!-- auto generated supported sources list -->'
REJECTED_SOURCE_LIST_QUE = '<!-- auto generated rejected sources list -->'

DATE_FORMAT = '%d %B %Y %I:%M:%S %p'
URL_REGEX = re.compile(r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', re.I)


def load_crawlers(file_path):
    file_path = Path(file_path)

    module_name = 'lncrawl_' + hashlib.md5(file_path.name.encode()).hexdigest()
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if not spec or not isinstance(spec.loader, FileLoader):
        raise Exception('No file loader module spec found')

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    crawler_list = []

    for key in dir(module):
        crawler = getattr(module, key)
        if type(crawler) == type(Crawler) and crawler.__base__ == Crawler:
            crawler_list.append(crawler)

    return crawler_list


def get_crawler_info(crawler):
    assert crawler

    assert 'base_url' in crawler.__dict__
    assert 'read_novel_info' in crawler.__dict__
    assert 'download_chapter_body' in crawler.__dict__

    can_login = 'login' in crawler.__dict__
    can_logout = 'logout' in crawler.__dict__
    can_search = 'search_novel' in crawler.__dict__

    urls = getattr(crawler, 'base_url')
    if isinstance(urls, str):
        urls = [urls]

    assert isinstance(urls, list)

    urls = [
        url.lower().strip('/') + '/'
        for url in set(urls)
        if URL_REGEX.match(url)
    ]

    assert len(urls) > 0

    return {
        'name': crawler.__name__,
        'can_search': can_search,
        'can_login': can_login,
        'can_logout': can_logout,
        'base_urls': urls,
    }


def git_last_commit_time(file_path):
    try:
        cmd = 'git log -1 --pretty="format:%%ct" "%s"' % file_path
        res = subprocess.check_output(cmd).decode('utf-8').strip()
        return int(res)
    except Exception:
        traceback.print_exc()
        return 0


def git_history(file_path):
    try:
        cmd = 'git log --follow --diff-filter=AMT --pretty="format:%%at||%%an||%%s" "%s"' % file_path
        logs = subprocess.check_output(cmd).decode('utf-8').strip()
        logs = [line.strip().split('||', maxsplit=3) for line in logs.splitlines(False)]
        logs = [{'time': int(x[0]), 'author': x[1], 'subject': x[2]} for x in logs]
        return logs
    except Exception:
        traceback.print_exc()
        return {}


def main():
    crawlers = {}
    index_data = {
        'app': {},
        'rejected': {},
        'supported': {},
        'crawlers': [],
    }

    #
    # Generate index data
    #

    assert SOURCES_FOLDER.is_dir()

    with open(REJECTED_FILE, encoding='utf8') as fp:
        rejected_sources = json.load(fp)

    def process_file(py_file: Path):
        if py_file.name[0] == '_':
            return

        relative_path = py_file.relative_to(WORKDIR).as_posix()
        print('Processing', relative_path)

        history = git_history(relative_path)
        download_url = SOURCE_DOWNLOAD_URL_PREFIX % relative_path

        for crawler in load_crawlers(py_file):
            info = get_crawler_info(crawler)
            info['url'] = download_url
            info['file_path'] = str(relative_path)
            info['version'] = history[0]['time']
            info['source'] = str(py_file.absolute())
            info['author'] = history[-1]['author']
            info['contributors'] = list(set([x['author'] for x in history]))
            info['last_commit'] = history[0]
            info['first_commit'] = history[-1]
            info['total_commits'] = len(history)
            info['id'] = hashlib.md5(download_url.encode()).hexdigest()

            crawlers[info['id']] = info
            for url in info['base_urls']:
                if url in rejected_sources:
                    index_data['rejected'][url] = rejected_sources[url]
                else:
                    index_data['supported'][url] = info['id']

    executor = ThreadPoolExecutor(10)
    futures = [
        executor.submit(process_file, py_file)
        for py_file in sorted(SOURCES_FOLDER.glob('**/*.py'))
    ]
    [f.result() for f in futures]
    executor.shutdown()

    index_data['crawlers'] = list(sorted(crawlers.values(), key=lambda x: (-x['version'])))

    print('%d crawlers.' % len(index_data['crawlers']),
          '%d supported urls.' % len(index_data['supported']),
          '%d rejected urls.' % len(index_data['rejected']))

    with open(INDEX_FILE, 'w', encoding='utf8') as fp:
        json.dump(index_data, fp, indent='  ')

    #
    # Update README.md
    #

    with open(README_FILE, encoding='utf8') as fp:
        readme_text = fp.read()

    before, supported, after = readme_text.split(SUPPORTED_SOURCE_LIST_QUE)
    supported = '\n\n<table>\n<tbody>\n'
    supported += '<tr>'
    supported += '<th>Source URL</th>\n'
    supported += '<th>Version</th>\n'
    supported += '<th>Search</th>\n'
    supported += '<th>Login</th>\n'
    supported += '<th>Created At</th>\n'
    supported += '<th>Contributors</th>\n'
    supported += '</tr>\n'
    for url, crawler_id in sorted(index_data['supported'].items()):
        info = crawlers[crawler_id]
        created_at = datetime.fromtimestamp(info['first_commit']['time']).strftime(DATE_FORMAT)
        history_url = 'https://github.com/dipu-bd/lightnovel-crawler/commits/master/%s' % info['file_path']
        supported += '<tr>'
        supported += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
        supported += '<td><a href="%s">📃 %s</a></td>\n' % (info['url'], info['version'])
        supported += '<td>%s</td>\n' % ('✔' if info['can_search'] else '')
        supported += '<td>%s</td>\n' % ('✔' if info['can_login'] else '')
        supported += '<td><a href="%s">%s</a></td>\n' % (history_url, created_at)
        supported += '<td>%s</td>\n' % ', '.join(sorted(info['contributors']))
        supported += '</tr>\n'
    supported += '</tbody>\n</table>\n\n'
    readme_text = SUPPORTED_SOURCE_LIST_QUE.join([before, supported, after])

    before, rejected, after = readme_text.split(REJECTED_SOURCE_LIST_QUE)
    rejected = '\n\n<table>\n<tbody>\n'
    rejected += '<tr>'
    rejected += '<th>Source URL</th>\n'
    rejected += '<th>Rejection Cause</th>\n'
    rejected += '</tr>\n'
    for url, cause in sorted(index_data['rejected'].items()):
        rejected += '<tr>'
        rejected += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
        rejected += '<td>%s</td>\n' % cause
        rejected += '</tr>\n'
    rejected += '</tbody>\n</table>\n\n'
    readme_text = REJECTED_SOURCE_LIST_QUE.join([before, rejected, after])

    with open(README_FILE, 'w', encoding='utf8') as fp:
        fp.write(readme_text)


if __name__ == '__main__':
    main()
