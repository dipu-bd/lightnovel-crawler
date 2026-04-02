#!/usr/bin/env python3
"""
Build lightnovel-crawler source index to use for update checking.
"""

import gzip
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Any, Dict, List
from urllib.parse import quote_plus, unquote_plus

import httpx

try:
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
    from lncrawl.assets.languages import language_codes
    from lncrawl.context import ctx
    from lncrawl.core import TaskManager
    from lncrawl.server.models import CrawlerInfo
except ImportError:
    raise

logger = logging.getLogger()

# =========================================================================================== #
# Configurations
# =========================================================================================== #

WORKDIR = Path(__file__).parent.parent.absolute()

SOURCES_FOLDER = WORKDIR / "sources"
INDEX_FILE = SOURCES_FOLDER / "_index.json"
INDEX_ZIP_FILE = SOURCES_FOLDER / "_index.zip"
CONTRIB_CACHE_FILE = WORKDIR / ".github" / "contribs.json"

README_FILE = WORKDIR / "README.md"
SUPPORTED_SOURCE_LIST_QUE = "<!-- auto generated supported sources list -->"
REJECTED_SOURCE_LIST_QUE = "<!-- auto generated rejected sources list -->"
HELP_RESULT_QUE = "<!-- auto generated command line output -->"

REPO_OWNER = "lncrawl"
REPO_NAME = "lightnovel-crawler"
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
FILE_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}"
WHEEL_RELEASE_URL = f"{REPO_URL}/releases/download/v%s/lightnovel_crawler-%s-py3-none-any.whl"

# =========================================================================================== #
# The index data
# =========================================================================================== #

session = httpx.Client(
    http2=True,
    verify=False,
    follow_redirects=True,
)

INDEX_DATA: Dict[str, Any] = {
    "v": int(time.time()),
    "app": {
        "windows": "https://go.bitanon.dev/lncrawl-windows",
        "linux": "https://go.bitanon.dev/lncrawl-linux",
    },
    "rejected": {},
    "supported": {},
    "crawlers": {},
}

try:
    logger.info("Getting latest app version")
    resp = session.get("https://pypi.org/pypi/lightnovel-crawler/json")
    resp.raise_for_status()
    pypi_data = resp.json()
    info = pypi_data["info"]
    logger.info(f"Latest version: {info['version']}")

    INDEX_DATA["app"]["version"] = info["version"]
    INDEX_DATA["app"]["home"] = info["home_page"]
    INDEX_DATA["app"]["pypi"] = info["release_url"]
except Exception:
    logger.error("Failed to get latest app data", exc_info=True)
    exit(1)

# =========================================================================================== #
# Generate sources index
# =========================================================================================== #

assert SOURCES_FOLDER.is_dir()

# Current git branch
try:
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    REPO_BRANCH = commit_hash.decode("utf-8").strip()
except Exception:
    logger.warning("Failed to get current git branch", exc_info=True)
    REPO_BRANCH = "dev"

github_cache_result: Dict[str, Any] = {}
github_cache_event: Dict[str, Event] = {}


def call_github_api(url):
    if url in github_cache_event:
        github_cache_event[url].wait()
        return github_cache_result[url]

    github_cache_event[url] = Event()
    for _ in range(3):
        resp = session.get(url)
        if resp.status_code == 200:
            github_cache_result[url] = resp.json()
        elif resp.status_code == 403 and "X-RateLimit-Reset" in resp.headers:
            reset_time = int(resp.headers["X-RateLimit-Reset"])
            sleep_seconds = max(0, reset_time - time.time()) + 1
            logger.info(f"[dim]Waiting {sleep_seconds:.0f} seconds[/dim]")
            time.sleep(sleep_seconds)
        else:
            break

    github_cache_event[url].set()
    return github_cache_result[url]


logger.info("Loading sources")
ctx.logger.setup(2)
ctx.config.load()
ctx.sources.load(False)
ctx.sources.ensure_load()

logger.info("Getting contributors")
repo_data = call_github_api("https://api.github.com/repos/lncrawl/lightnovel-crawler/contributors")
repo_contribs = {x["login"]: x for x in repo_data}

logger.info("Loading username cache")
username_cache = {}
try:
    username_cache = json.loads(CONTRIB_CACHE_FILE.read_text(encoding="utf-8"))
except Exception:
    logger.error("Could not load username cache", exc_info=True)


def search_user_by(query):
    try:
        data = call_github_api(f"https://api.github.com/search/users?q={query}")
        for item in data["items"]:
            login = item["login"]
            if login in repo_contribs:
                logger.info(f"Search result: {unquote_plus(query)} | {login}")
                return login
    except Exception:
        logger.warning(f"Failed to resolve user by query: {query}", exc_info=True)
        return ""


def git_history(file_path, sep="|~|") -> List[Dict[Any, Any]]:
    result = []
    try:
        # cmd = f'git log -1 --diff-filter=ACMT --pretty="%at{sep}%aN{sep}%aE{sep}%s" "{file_path}"'
        cmd = f'git log --follow --diff-filter=ACMT --pretty="%at{sep}%aN{sep}%aE{sep}%s" "{file_path}"'
        logs = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        for line in logs.splitlines(False):
            rows = line.strip().split(sep, maxsplit=4)
            if len(rows) == 4:
                result.append(
                    {
                        "time": int(rows[0]),
                        "author": rows[1],
                        "email": rows[2],
                        "subject": rows[3],
                    }
                )
    except Exception:
        logger.warning(f"Failed to get git history: {file_path}", exc_info=True)
    return result


def process_contributors(history):
    contribs = set([])
    for data in history:
        author = data["author"]
        email = data["email"]
        if author in username_cache:
            contribs.add(username_cache[author])
            continue
        if email in username_cache:
            contribs.add(username_cache[email])
            continue
        if author in repo_contribs:
            username_cache[author] = author
            username_cache[email] = author
            contribs.add(author)
            continue
        if session.head(f"https://github.com/{author}/{REPO_NAME}").status_code == 200:
            username_cache[author] = author
            username_cache[email] = author
            contribs.add(author)
            continue
        name = search_user_by(quote_plus(f"{email} in:email"))
        if name in repo_contribs:
            username_cache[author] = name
            username_cache[email] = name
            contribs.add(name)
            continue
        name = search_user_by(quote_plus(f"{author} in:name"))
        if name in repo_contribs:
            username_cache[author] = name
            username_cache[email] = name
            contribs.add(name)
            continue
        username_cache[author] = None
        username_cache[email] = None
    return list(sorted(filter(None, contribs)))


def process_info(info: CrawlerInfo):
    py_file = info.local_file
    relative_path = py_file.relative_to(WORKDIR).as_posix()
    logger.info(f"[cyan]{info.id}[/cyan] {relative_path}")

    info.md5 = hashlib.md5(py_file.read_bytes()).hexdigest()
    info.url = f"{FILE_DOWNLOAD_URL}/{REPO_BRANCH}/{relative_path}"

    history = git_history(relative_path)
    if history:
        info.total_commits = len(history)
        info.version = history[0]["time"]
        info.contributors = process_contributors(history)

    INDEX_DATA["crawlers"][info.id] = info.model_dump()
    for url in info.base_urls:
        reason = ctx.sources.is_rejected(url)
        if reason:
            INDEX_DATA["rejected"][url] = reason
        else:
            INDEX_DATA["supported"][url] = info.id


logger.info("Loading crawlers")
futures = []
visited = set()
taskman = TaskManager(42)
ctx.sources._taskman = taskman
for info in ctx.sources.load_crawlers(*sorted(SOURCES_FOLDER.glob("**/*.py"))):
    if info.id in visited:
        continue
    visited.add(info.id)
    task = taskman.submit_task(process_info, info)
    futures.append(task)
taskman.resolve_futures(futures, disable_bar=True)
taskman.close()

INDEX_DATA["crawlers"] = dict(sorted(INDEX_DATA["crawlers"].items()))
INDEX_DATA["rejected"] = dict(sorted(INDEX_DATA["rejected"].items()))
INDEX_DATA["supported"] = dict(sorted(INDEX_DATA["supported"].items()))

logger.info(
    f"{len(INDEX_DATA['crawlers'])} crawlers. "
    f"{len(INDEX_DATA['supported'])} supported urls. "
    f"{len(INDEX_DATA['rejected'])} rejected urls."
)

logger.info("Saving index files")
index_file_content = json.dumps(INDEX_DATA, indent=2, ensure_ascii=False).encode()
INDEX_FILE.write_bytes(index_file_content)

minified_index_file_content = json.dumps(INDEX_DATA, ensure_ascii=False).encode()
INDEX_ZIP_FILE.write_bytes(gzip.compress(minified_index_file_content))

username_cache_content = json.dumps(username_cache, indent=2, ensure_ascii=False).encode()
CONTRIB_CACHE_FILE.write_bytes(username_cache_content)

# =========================================================================================== #
# Update README.md
# =========================================================================================== #

# Make groups by language codes
grouped_crawlers: Dict[Any, Any] = {}
grouped_supported: Dict[Any, Any] = {}

for crawler_id, crawler in INDEX_DATA["crawlers"].items():
    ln_code = crawler["file_path"].split("/")[1]
    if ln_code not in language_codes:
        ln_code = ""
    grouped_crawlers[crawler_id] = ln_code

for link, crawler_id in INDEX_DATA["supported"].items():
    ln_code = grouped_crawlers[crawler_id]
    grouped_supported.setdefault(ln_code, {})
    grouped_supported[ln_code][link] = crawler_id

logger.info("Rendering supported and rejected source list for README.md")

with open(README_FILE, encoding="utf8") as fp:
    readme_text = fp.read()

before, supported, after = readme_text.split(SUPPORTED_SOURCE_LIST_QUE)

supported = "\n\n"
supported += f"We are supporting {len(INDEX_DATA['supported'])} sources and {len(INDEX_DATA['crawlers'])} crawlers."

for ln_code, links in sorted(grouped_supported.items(), key=lambda x: x[0]):
    assert isinstance(links, dict)
    language = language_codes.get(ln_code, "Unknown")
    supported += "\n\n"
    supported += f"### `{ln_code or '~'}` {language}"
    supported += "\n\n"
    supported += "<table>\n<tbody>\n"
    supported += "<tr>"
    supported += "<th></th>\n"
    supported += "<th>Source URL</th>\n"
    supported += "<th>Version</th>\n"
    # supported += '<th>Created At</th>\n'
    supported += "<th>Contributors</th>\n"
    supported += "</tr>\n"
    for url, crawler_id in sorted(links.items(), key=lambda x: x[0]):
        info = INDEX_DATA["crawlers"][crawler_id]
        source_url = f"{REPO_URL}/blob/{REPO_BRANCH}/{info['file_path']}"
        last_update = (
            datetime.fromtimestamp(info["version"])
            .astimezone(timezone.utc)
            .strftime(
                "%d %B %Y %I:%M:%S %p (UTC+0)",
            )
        )

        supported += "<tr>"

        supported += "<td>"
        supported += '<span title="Contains machine translations">%s</span>' % (
            "🤖" if info["has_mtl"] else ""
        )
        supported += '<span title="Supports searching">%s</span>' % (
            "🔍" if info["can_search"] else ""
        )
        supported += '<span title="Supports login">%s</span>' % ("🔑" if info["can_login"] else "")
        supported += '<span title="Contains manga/manhua/manhwa">%s</span>' % (
            "🖼️" if info["has_manga"] else ""
        )
        supported += "</td>\n"

        supported += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
        supported += '<td><a href="%s" title="%s">%d</a></td>\n' % (
            source_url,
            last_update,
            info["total_commits"],
        )
        supported += "<td>%s</td>\n" % " ".join(
            [
                '<a href="%s"><img src="%s&s=24" alt="%s" height="24"/></a>'
                % (c["html_url"], c["avatar_url"], c["login"])
                for c in sorted(
                    [repo_contribs[x] for x in info["contributors"] if x in repo_contribs],
                    key=lambda x: -x["contributions"],
                )
            ]
        )
        supported += "</tr>\n"
    supported += "</tbody>\n</table>\n"

readme_text = SUPPORTED_SOURCE_LIST_QUE.join([before, supported, after])

logger.info("Generated supported sources list.")

before, rejected, after = readme_text.split(REJECTED_SOURCE_LIST_QUE)
rejected = "\n\n"
rejected += f"We have rejected {len(INDEX_DATA['rejected'])} sources due to the following reasons."
rejected = "\n\n"
rejected += "<table>\n<tbody>\n"
rejected += "<tr>"
rejected += "<th>Source URL</th>\n"
rejected += "<th>Rejection Cause</th>\n"
rejected += "</tr>\n"
for url, cause in sorted(INDEX_DATA["rejected"].items(), key=lambda x: x[0]):
    rejected += "<tr>"
    rejected += '<td><a href="%s" target="_blank">%s</a></td>\n' % (url, url)
    rejected += "<td>%s</td>\n" % cause
    rejected += "</tr>\n"
rejected += "</tbody>\n</table>\n\n"
readme_text = REJECTED_SOURCE_LIST_QUE.join([before, rejected, after])

logger.info("Generated rejected sources list.")

before, help_text, after = readme_text.split(HELP_RESULT_QUE)

output = subprocess.check_output(
    [sys.executable, "lncrawl", "-h"],
    cwd=WORKDIR,
).decode("utf-8")
output = re.sub(r"\x1b\[[0-9;\r]*m", "", output.strip())

help_text = "\n"
help_text += "```text\n"
help_text += "$ lncrawl -h\n"
help_text += output
help_text += "\n```\n"

readme_text = HELP_RESULT_QUE.join([before, help_text, after])

logger.info("Generated help command output.")
README_FILE.write_bytes(readme_text.encode())
