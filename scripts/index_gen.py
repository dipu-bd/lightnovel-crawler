#!/usr/bin/env python3
"""
Build lightnovel-crawler source index to use for update checking.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from threading import Event
from typing import Dict
from urllib.parse import quote_plus, unquote_plus

try:
    import cloudscraper
except ImportError:
    print("cloudscraper not found")
    exit(1)

try:
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))
    from lncrawl.assets.languages import language_codes
    from lncrawl.core.crawler import Crawler
except ImportError:
    print("lncrawl not found")
    exit(1)

# =========================================================================================== #
# Configurations
# =========================================================================================== #

WORKDIR = Path(__file__).parent.parent.absolute()

SOURCES_FOLDER = WORKDIR / "sources"
INDEX_FILE = SOURCES_FOLDER / "_index.json"
REJECTED_FILE = SOURCES_FOLDER / "_rejected.json"
CONTRIB_CACHE_FILE = WORKDIR / ".github" / "contribs.json"

README_FILE = WORKDIR / "README.md"
SUPPORTED_SOURCE_LIST_QUE = "<!-- auto generated supported sources list -->"
REJECTED_SOURCE_LIST_QUE = "<!-- auto generated rejected sources list -->"
HELP_RESULT_QUE = "<!-- auto generated command line output -->"

DATE_FORMAT = "%d %B %Y %I:%M:%S %p"

REPO_BRANCH = "master"
REPO_OWNER = 'dipu-bd'
REPO_NAME = 'lightnovel-crawler'
REPO_URL = f"https://github.com/{REPO_OWNER}/{REPO_NAME}"
FILE_DOWNLOAD_URL = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}"
WHEEL_RELEASE_URL = f"{REPO_URL}/releases/download/v%s/lightnovel_crawler-%s-py3-none-any.whl"

# Current git branch
try:
    commit_hash = subprocess.check_output(["git", "rev-parse", "HEAD"])
    REPO_BRANCH = commit_hash.decode("utf-8").strip()
except Exception:
    traceback.print_exc()

# =========================================================================================== #
# The index data
# =========================================================================================== #

session = cloudscraper.create_scraper()

INDEX_DATA = {
    "v": int(time.time()),
    "app": {
        "windows": "https://rebrand.ly/lncrawl",
        "linux": "https://rebrand.ly/lncrawl-linux",
    },
    "rejected": {},
    "supported": {},
    "crawlers": {},
}

print("-" * 50)
res = session.get("https://pypi.org/pypi/lightnovel-crawler/json")
res.raise_for_status()
pypi_data = res.json()
print("Latest version:", pypi_data["info"]["version"])

INDEX_DATA["app"]["version"] = pypi_data["info"]["version"]
INDEX_DATA["app"]["home"] = pypi_data["info"]["home_page"]
INDEX_DATA["app"]["pypi"] = pypi_data["info"]["release_url"]
print("-" * 50)


# =========================================================================================== #
# Generate sources index
# =========================================================================================== #

executor = ThreadPoolExecutor(8)
queue_cache_result: Dict[str, str] = {}
queue_cache_event: Dict[str, Event] = {}

try:
    sys.path.insert(0, str(WORKDIR))
    from lncrawl.core.sources import __import_crawlers
except ImportError:
    traceback.print_exc()
    exit(1)

assert SOURCES_FOLDER.is_dir()

with open(REJECTED_FILE, encoding="utf8") as fp:
    rejected_sources = json.load(fp)

username_cache = {}
try:
    with open(CONTRIB_CACHE_FILE, encoding="utf8") as fp:
        username_cache = json.load(fp)
except Exception as e:
    print("Could not load contributor cache file", e)


print("Getting contributors...")
res = session.get(
    "https://api.github.com/repos/dipu-bd/lightnovel-crawler/contributors"
)
res.raise_for_status()
repo_contribs = {x["login"]: x for x in res.json()}
print("Contributors:", ", ".join(repo_contribs.keys()))
print("-" * 50)


def search_user_by(query):
    if query in queue_cache_event:
        queue_cache_event[query].wait()
        return queue_cache_result.get(query, "")

    queue_cache_event[query] = Event()
    for _ in range(2):
        res = session.get("https://api.github.com/search/users?q=%s" % query)
        if res.status_code != 200:
            current_limit = int(res.headers.get("X-RateLimit-Remaining") or "0")
            if current_limit == 0:
                reset_time = (
                    int(res.headers.get("X-RateLimit-Reset") or "0") - time.time()
                )
                print(query, ":", "Waiting %d seconds for reset..." % reset_time)
                time.sleep(reset_time + 2)
            continue
        data = res.json()
        for item in data["items"]:
            if item["login"] in repo_contribs:
                print("search result:", unquote_plus(query), "|", item["login"])
                queue_cache_result[query] = item["login"]
                break
        break
    queue_cache_event[query].set()
    return queue_cache_result.get(query, "")


def git_history(file_path):
    try:
        # cmd = f'git log -1 --diff-filter=ACMT --pretty="%at||%aN||%aE||%s" "{file_path}"'
        cmd = f'git log --follow --diff-filter=ACMT --pretty="%at||%aN||%aE||%s" "{file_path}"'
        logs = subprocess.check_output(cmd, shell=True).decode("utf-8").strip()
        logs = [
            {
                "time": int(x[0]),
                "author": x[1],
                "email": x[2],
                "subject": x[3]
            }
            for x in [
                line.strip().split("||", maxsplit=4)
                for line in logs.splitlines(False)
            ]
        ]
        return logs
    except Exception:
        traceback.print_exc()
        return {}


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
        if session.head(f'https://github.com/{author}/{REPO_NAME}').status_code == 200:
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
        # contribs.add(author)
    return list(filter(None, contribs))


def process_file(py_file: Path) -> float:
    if py_file.name.startswith("_") or not py_file.name[0].isalnum():
        return 0

    start = time.time()
    relative_path = py_file.relative_to(WORKDIR).as_posix()
    download_url = f"{FILE_DOWNLOAD_URL}/{REPO_BRANCH}/{relative_path}"

    history = git_history(relative_path)

    with open(py_file, "rb") as f:
        md5 = hashlib.md5(f.read()).hexdigest()

    for crawler in __import_crawlers(py_file):
        can_login = Crawler.login != crawler.login
        can_logout = Crawler.logout != crawler.logout
        can_search = Crawler.search_novel != crawler.search_novel
        has_manga = getattr(crawler, "has_manga", False)
        has_mtl = getattr(crawler, "has_mtl", False)
        source_id = hashlib.md5(str(crawler).encode("utf8")).hexdigest()

        # Test crawler instance
        crawler()

        # Gather crawler info
        info = {}
        info["id"] = source_id
        info["md5"] = md5
        info["url"] = download_url
        # info['name'] = crawler.__name__
        # info['filename'] = py_file.name
        info["version"] = history[0]["time"]
        info["total_commits"] = len(history)
        info["file_path"] = str(relative_path)
        # info['last_commit'] = history[0]
        # info['first_commit'] = history[-1]
        # info['author'] = history[-1]['author']
        info["has_mtl"] = has_mtl
        info["has_manga"] = has_manga
        info["can_search"] = can_search
        info["can_login"] = can_login
        info["can_logout"] = can_logout
        info["base_urls"] = getattr(crawler, "base_url")
        info["contributors"] = process_contributors(history)

        INDEX_DATA["crawlers"][source_id] = info
        for url in info["base_urls"]:
            if url in rejected_sources:
                INDEX_DATA["rejected"][url] = rejected_sources[url]
            else:
                INDEX_DATA["supported"][url] = source_id

    return time.time() - start


futures = {}
for py_file in sorted(SOURCES_FOLDER.glob("**/*.py")):
    futures[py_file] = executor.submit(process_file, py_file)
for py_file, future in futures.items():
    print("> %-40s" % py_file.name, end="")
    runtime = future.result()
    print("%.3fs" % runtime)

print("-" * 50)
print(
    "%d crawlers." % len(INDEX_DATA["crawlers"]),
    "%d supported urls." % len(INDEX_DATA["supported"]),
    "%d rejected urls." % len(INDEX_DATA["rejected"]),
)
print("-" * 50)

with open(INDEX_FILE, "w", encoding="utf8") as fp:
    json.dump(INDEX_DATA, fp)  # , indent='  ')

with open(CONTRIB_CACHE_FILE, "w", encoding="utf8") as fp:
    json.dump(username_cache, fp, indent="  ")

# =========================================================================================== #
# Update README.md
# =========================================================================================== #

# Make groups by language codes
grouped_crawlers = dict()
grouped_supported = dict()

for crawler_id, crawler in INDEX_DATA["crawlers"].items():
    ln_code = crawler["file_path"].split("/")[1]
    if ln_code not in language_codes:
        ln_code = ""
    grouped_crawlers[crawler_id] = ln_code

for link, crawler_id in INDEX_DATA["supported"].items():
    ln_code = grouped_crawlers[crawler_id]
    grouped_supported.setdefault(ln_code, {})
    grouped_supported[ln_code][link] = crawler_id

print("Rendering supported and rejected source list for README.md...")

with open(README_FILE, encoding="utf8") as fp:
    readme_text = fp.read()

before, supported, after = readme_text.split(SUPPORTED_SOURCE_LIST_QUE)

supported = "\n\n"
supported += f"We are supporting {len(INDEX_DATA['supported'])} sources and {len(INDEX_DATA['crawlers'])} crawlers."

for ln_code, links in sorted(grouped_supported.items(), key=lambda x: x[0]):
    assert isinstance(links, dict)
    language = language_codes.get(ln_code, "Unknown")
    supported += "\n\n"
    supported += f'### `{ln_code or "~"}` {language}'
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
        last_update = datetime.fromtimestamp(info["version"]).strftime(DATE_FORMAT)

        supported += "<tr>"

        supported += "<td>"
        supported += '<span title="Contains machine translations">%s</span>' % (
            "🤖" if info["has_mtl"] else ""
        )
        supported += '<span title="Supports searching">%s</span>' % (
            "🔍" if info["can_search"] else ""
        )
        supported += '<span title="Supports login">%s</span>' % (
            "🔑" if info["can_login"] else ""
        )
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
                    [
                        repo_contribs[x]
                        for x in info["contributors"]
                        if x in repo_contribs
                    ],
                    key=lambda x: -x["contributions"],
                )
            ]
        )
        supported += "</tr>\n"
    supported += "</tbody>\n</table>\n"

readme_text = SUPPORTED_SOURCE_LIST_QUE.join([before, supported, after])

print("Generated supported sources list.")

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

print("Generated supported sources list.")

before, help_text, after = readme_text.split(HELP_RESULT_QUE)

os.chdir(WORKDIR)
output = subprocess.check_output(["python", "lncrawl", "-h"])

help_text = "\n"
help_text += "```bash\n"
help_text += "$ lncrawl -h\n"
help_text += output.decode("utf-8").replace("\r\n", "\n")
help_text += "```\n"

readme_text = HELP_RESULT_QUE.join([before, help_text, after])

print("Generated help command output.")

with open(README_FILE, "w", encoding="utf8") as fp:
    fp.write(readme_text)

print("-" * 50)

executor.shutdown()
