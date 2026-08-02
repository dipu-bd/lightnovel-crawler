# Lightnovel Crawler

[![download win](https://img.shields.io/badge/download-lncrawl.exe-red?logo=windows&style=for-the-badge)](https://go.bitanon.dev/lncrawl-windows)
[![download linux](<https://img.shields.io/badge/download-lncrawl_(linux)-brown?logo=linux&style=for-the-badge>)](https://go.bitanon.dev/lncrawl-linux)
[![download mac](<https://img.shields.io/badge/download-lncrawl_(mac)-blue?logo=apple&style=for-the-badge>)](https://go.bitanon.dev/lncrawl-mac)
<br>
[![PyPI version](https://img.shields.io/pypi/v/lightnovel-crawler.svg?logo=python)](https://pypi.org/project/lightnovel-crawler)
[![Python version](https://img.shields.io/pypi/pyversions/lightnovel-crawler.svg)](https://pypi.org/project/lightnovel-crawler)
[![Downloads](https://pepy.tech/badge/lightnovel-crawler)](https://pepy.tech/project/lightnovel-crawler)
[![License](https://img.shields.io/badge/license-GPLv3-blue.svg)](https://github.com/lncrawl/lightnovel-crawler/blob/master/LICENSE)
<br>
[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/lncrawl/lightnovel-crawler)
[![Lint](https://github.com/lncrawl/lightnovel-crawler/actions/workflows/lint.yml/badge.svg)](https://github.com/lncrawl/lightnovel-crawler/actions/workflows/lint.yml)
[![Build and Publish](https://github.com/lncrawl/lightnovel-crawler/actions/workflows/release.yml/badge.svg)](https://github.com/lncrawl/lightnovel-crawler/actions/workflows/release.yml)

**Lightnovel Crawler** downloads web novels and similar fiction from hundreds of online reading sites and saves them as e-books — so you can read offline on your phone, tablet, or e-reader.

- Download a story you follow as a single EPUB instead of bookmarking hundreds of web pages.
- Run a private home server to collect and read all your novels in one place.

> **Personal use only.** Sites publish fiction under their own terms and copyright. Only use this tool for personal backups of content you have legitimate access to. Do not redistribute or sell someone else's work.

## Quick Start

| I want to…        | How                                     |
| ----------------- | --------------------------------------- |
| Just try it       | [Download the executable](#-standalone) |
| Use the CLI       | [pip install](#-pip)                    |
| Run a home server | [Docker](#-docker)                      |

Once it's running: open **http://localhost:8181**, sign in with `admin` / `admin`, and paste a novel URL to download it.

## Installation

<a href="https://github.com/lncrawl/lightnovel-crawler"><img src="res/lncrawl-icon.png" width="128px" align="right"/></a>

Pick **one** of the three methods below.

### ⏬ Standalone

Download and run — no Python required.

| Platform | Download                                                 |
| -------- | -------------------------------------------------------- |
| Windows  | [📦 lncrawl.exe](https://go.bitanon.dev/lncrawl-windows) |
| Linux    | [📦 lncrawl](https://go.bitanon.dev/lncrawl-linux)       |
| macOS    | [📦 lncrawl](https://go.bitanon.dev/lncrawl-mac)         |

_Check [Releases](https://github.com/lncrawl/lightnovel-crawler/releases) for older versions._

**Windows:** Double-click the downloaded `.exe`. SmartScreen may warn about an unknown app — click "More info → Run anyway". Setup is required before first run.

**macOS / Linux:** No setup needed. Make the file executable and run it:

```bash
chmod +x lncrawl
./lncrawl
```

[![Tutorial](res/screenshots/tutorial.png)](res/screenshots/tutorial.png)

### 📦 pip

Requires Python 3.9+.

```bash
pip install -U lightnovel-crawler
```

_If it fails, try `python -m pip install -U lightnovel-crawler`._

To install directly from GitHub:

```bash
# Latest stable
pip install -U git+https://github.com/lncrawl/lightnovel-crawler.git#egg=lightnovel-crawler

# Development branch (latest fixes but unstable)
pip install -U https://github.com/lncrawl/lightnovel-crawler/tarball/refs/heads/dev#egg=lightnovel-crawler
```

Verify the install:

```bash
lncrawl -h
```

_If `lncrawl` is not found, use `python -m lncrawl -h` instead._

<!-- auto generated command line output -->
```text
$ lncrawl -h
Usage: lncrawl [OPTIONS] COMMAND [ARGS]...                                     
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --verbose             -l              Log levels: -l = warn, -ll = info,     │
│                                       -lll = debug                           │
│ --config              -c      <path>  Config file                            │
│ --install-completion                  Install completion for the current     │
│                                       shell.                                 │
│ --show-completion                     Show completion for the current shell, │
│                                       to copy it or customize the            │
│                                       installation.                          │
│ --help                -h              Show this message and exit.            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ app      Launches the web application.                                       │
│ version  Show current version.                                               │
│ dev      Run development commands.                                           │
│ config   View and modify configuration settings.                             │
│ sources  Manage sources.                                                     │
│ crawl    Crawl from novel page URL.                                          │
│ search   Search for novels by query string.                                  │
│ server   Run web server.                                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
```
<!-- auto generated command line output -->

### 🐳 Docker

Requires [Docker](https://www.docker.com/get-started/).

```bash
mkdir -p lncrawl-data
docker pull ghcr.io/lncrawl/lightnovel-crawler
docker run -v ./lncrawl-data:/data -it -p 8181:8181 -e TZ=Europe/London \
  --name lncrawl-server ghcr.io/lncrawl/lightnovel-crawler -ll server
```

Set `TZ` to the zone your internet address looks like it is in — see [above](#when-a-site-says-no) for why it matters more than it sounds.

Then open **http://localhost:8181** and sign in with `admin` / `admin`.

[![Login](res/screenshots/login.png)](res/screenshots/login.png)

---

## Using the App

### Web interface

The web UI lets you browse, download, and read novels without touching the command line.

**Start the server:**

- **Standalone / pip:** run `lncrawl server`.
- **Docker:** the server starts with the `docker run` command above.

**Open in browser:** Visit **http://localhost:8181**.

**First-time login:** `admin` / `admin`. Change your password in **Settings → Account**.

**Downloading a novel:**

1. Go to **Crawlers** to browse supported sites, or paste a novel URL directly into the search bar.
2. Select the chapters you want (a range or all of them).
3. Choose an output format (see [Output Formats](#output-formats) below).
4. Click **Download** — track progress on the **Requests** page.
5. Open the result in the built-in **Reader**, or download the file to your device.

**Library:** Save novels to your Library to re-download new chapters with one click whenever the story updates.

[![Crawlers](res/screenshots/crawlers.png)](res/screenshots/crawlers.png)
[![Requests](res/screenshots/requests.png)](res/screenshots/requests.png)
[![Novels](res/screenshots/novels.png)](res/screenshots/novels.png)
[![Reader](res/screenshots/reader.png)](res/screenshots/reader.png)
[![Libraries](res/screenshots/libraries.png)](res/screenshots/libraries.png)
[![Settings](res/screenshots/settings.png)](res/screenshots/settings.png)

**Common examples:**

```bash
# Open as application (no login)
lncrawl app

# Run as a server (has login)
lncrawl server

# Download the first 10 chapters as EPUB
lncrawl crawl "https://example.com/novel/page" -f epub --first 10

# Download all chapters
lncrawl crawl "https://example.com/novel/page" -f epub --all

# Search by title
lncrawl search "The Beginning After The End"
```

_Use a URL from any [supported source](#supported-sources)._

---

## Output Formats

| Format      | Needs Calibre | Best for                        |
| ----------- | :-----------: | ------------------------------- |
| 📚 **EPUB** |               | Most e-readers and reading apps |
| 📃 **TXT**  |               | Simple reading, any text editor |
| 🗂️ **JSON** |               | Scripts and developers          |
| 📄 **PDF**  |       ✓       | Print-ready, universal          |
| 🔳 **AZW3** |       ✓       | Kindle (current)                |
| 🔲 **MOBI** |       ✓       | Kindle (older devices)          |
| 📝 **DOCX** |       ✓       | Word, LibreOffice               |
| 📑 **RTF**  |       ✓       | WordPad and others              |
| 📔 **FB2**  |       ✓       | FB2 readers                     |
| 📕 **LIT**  |       ✓       | MS Reader (obsolete)            |
| 📗 **LRF**  |       ✓       | Sony readers                    |
| 🗄️ **PDB**  |       ✓       | PalmOS (legacy)                 |
| 📘 **RB**   |       ✓       | RocketBook/REB1100              |
| 📙 **TCR**  |       ✓       | Psion readers                   |

### Calibre (optional)

Install [Calibre](https://calibre-ebook.com/download) to unlock the formats marked above.

- **macOS / Linux:** No extra configuration — `ebook-convert` is detected automatically after installing Calibre.
- **Windows:** After installing, add the Calibre folder to your `Path` (default: `C:\Program Files\Calibre2`).

---

## Contributing

Contributions are welcome — bug fixes, new sources, documentation, and more.

![Repobeats](https://repobeats.axiom.co/api/embed/ecf3e93f676c27ba6404315e22523033d50aab45.svg "Repobeats analytics image")

See [**CONTRIBUTING.md**](.github/CONTRIBUTING.md) for setup instructions, code style, and how to add a source crawler.

- [CI on forks](.github/FORKING.md)
- [AI-assisted project overview (DeepWiki)](https://deepwiki.com/lncrawl/lightnovel-crawler)

### Local dev setup

Install [uv](https://docs.astral.sh/uv/) first (or let `make setup` install it for you).

```bash
git clone https://github.com/lncrawl/lightnovel-crawler.git
cd lightnovel-crawler
make install   # install uv + syncs dependencies
make start     # runs the dev server
```

Or with uv directly:

```bash
uv sync --all-extras --all-groups
uv run python -m lncrawl -ll server
```

<details>
<summary>Full Makefile reference</summary>

```bash
# Setup
make setup            # install uv
make install          # setup + uv sync (default: `make`)
make sync             # uv sync only
make upgrade          # setup + uv sync --upgrade

# Dev
make start            # Run dev server
make watch            # Run with auto-reload
make lint             # ruff format and check

# Version (writes lncrawl/VERSION)
make patch            # bump patch version
make minor            # bump minor version
make major            # bump major version

# Build
make build            # Full build: wheel + exe
make build-wheel      # Python wheel only
make build-exe        # PyInstaller exe only

# Dependencies
make add-dep <pkg>    # Add runtime dependency
make add-dev <pkg>    # Add dev dependency
make rm-dep <pkg>     # Remove runtime dependency
make rm-dev <pkg>     # Remove dev dependency

# Docker
make docker-build     # Build base + app images
make docker-up        # docker compose up -d
make docker-down      # docker compose down
make docker-logs      # docker compose logs -f

# Misc
make clean            # Remove .venv, build artifacts, caches
make version          # Print current version
```

</details>

---

## When a site says no

Most of these sites sit behind bot detection, and a downloader that answers a block by retrying harder is a downloader that quietly stops working. This one reads _what_ is blocking before it reacts.

- **It escalates only as far as it has to.** A plain request first, a different address when the block is about where you came from, a real browser only when a challenge genuinely needs one. Rotating the proxy at a rate limit is the reflex that makes things worse — the new address gets throttled just the same, because the pacing was the problem.
- **Challenges are solved in a browser you already have.** Firefox for preference, Chrome as the fallback, hidden by default. The clearance is reused, so one solve covers a whole book instead of one page.
- **An empty page is a failure, not a success.** A challenge screen and a page of adverts both answer `200`. Parsed as a chapter they produce a download that reports success and contains nothing, which is the most common way a source breaks.

Ask what it knows about any site:

```console
$ lncrawl dev explain https://aquareader.org/
aquareader.org
  binding layer : L9 Managed JavaScript challenge — reads a hybrid property, solve
  tier          : direct (unproven)
  pacing        : 3.0s mean interval
  requests      : 0 ok / 5 failed
  clearance     : none
  ladder        : archive(0) direct(10)
  exits         : direct
```

When a download fails you get that, not `403 after 3 retries` — which layer is blocking, what it reads, and whether anything you can configure would move it. A block on your address is answered by adding a proxy. A block that wants an account cannot be talked around, and it says so rather than retrying for an hour.

The engine is [`lncrawl-scraper`](https://github.com/lncrawl/scraper), built and measured against a corpus of ~300 real source hosts.

> **Running in Docker? Set `TZ`.** A container's clock is UTC, and a browser whose timezone disagrees with where its address geolocates reads as a robot. Measured in this image: **1 of 3 challenged sites cleared on the default clock, 3 of 3 with `TZ` set** to the zone your address looks like it is in.

**What it will not do:** log into a site for you, pay a captcha-solving service, or pretend a site is reachable when it is not.

---

### Adding a new source

Copy one of the example file from [sources/\_examples/](sources/_examples) into `sources/{lang}/` and implement the required methods.

Full guide: [.github/docs/CREATING_CRAWLERS.md](.github/docs/CREATING_CRAWLERS.md)

---

## Supported Sources

To request a new source, please [create an issue](https://github.com/lncrawl/lightnovel-crawler/issues/new/choose).

<details>
<summary>Click to expand</summary>

<!-- auto generated supported sources list -->

We are supporting 339 sources and 422 crawlers.

### `~` Unknown

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://es.mtlnovel.com/" target="_blank">http://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://es.mtlnovels.com/" target="_blank">http://es.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://fr.mtlnovel.com/" target="_blank">http://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://fr.mtlnovels.com/" target="_blank">http://fr.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://id.mtlnovel.com/" target="_blank">http://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://id.mtlnovels.com/" target="_blank">http://id.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.mtlnovel.com/" target="_blank">http://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://www.mtlnovels.com/" target="_blank">http://www.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://18.foxaholic.com/" target="_blank">https://18.foxaholic.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/foxaholic.py" title="23 July 2026 05:56:51 PM (UTC+0)">85</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://es.mtlnovel.com/" target="_blank">https://es.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://es.mtlnovels.com/" target="_blank">https://es.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://foxaholic.com/" target="_blank">https://foxaholic.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/foxaholic.py" title="23 July 2026 05:56:51 PM (UTC+0)">85</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fr.mtlnovel.com/" target="_blank">https://fr.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fr.mtlnovels.com/" target="_blank">https://fr.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://global.foxaholic.com/" target="_blank">https://global.foxaholic.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/foxaholic.py" title="23 July 2026 05:56:51 PM (UTC+0)">85</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://id.mtlnovel.com/" target="_blank">https://id.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://id.mtlnovels.com/" target="_blank">https://id.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://my.w.tt/" target="_blank">https://my.w.tt/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/wattpad.py" title="16 May 2026 04:51:10 PM (UTC+0)">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wtr-lab.com/" target="_blank">https://wtr-lab.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/wtrlab.py" title="31 July 2026 06:33:24 PM (UTC+0)">25</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxaholic.com/" target="_blank">https://www.foxaholic.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/foxaholic.py" title="23 July 2026 05:56:51 PM (UTC+0)">85</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlnovel.com/" target="_blank">https://www.mtlnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mtlnovels.com/" target="_blank">https://www.mtlnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/mtlnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">31</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelupdates.com/" target="_blank">https://www.novelupdates.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/novelupdates.py" title="23 July 2026 06:59:30 PM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.quotev.com/" target="_blank">https://www.quotev.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/quotev.py" title="01 April 2026 05:15:05 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wattpad.com/" target="_blank">https://www.wattpad.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/wattpad.py" title="16 May 2026 04:51:10 PM (UTC+0)">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webfic.com/" target="_blank">https://www.webfic.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/multi/webfic.py" title="06 May 2026 05:05:04 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `ar` Arabic

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://kolnovel.com/" target="_blank">https://kolnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ar/kolnovel.py" title="23 February 2023 12:26:02 AM (UTC+0)">1</a></td>
<td></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rewayat.club/" target="_blank">https://rewayat.club/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ar/rewayatclub.py" title="12 June 2026 08:44:54 PM (UTC+0)">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sunovels.com/" target="_blank">https://sunovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ar/sunovels.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `en` English

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://lightnovels.live/" target="_blank">http://lightnovels.live/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelme.py" title="09 May 2026 06:08:01 PM (UTC+0)">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://novelfull.com/" target="_blank">http://novelfull.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfull.py" title="26 March 2024 06:17:03 AM (UTC+0)">50</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://readlightnovel.online/" target="_blank">http://readlightnovel.online/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelreader.py" title="02 April 2026 04:44:44 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://readonlinenovels.com/" target="_blank">http://readonlinenovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readonlinenovels.py" title="01 April 2026 05:15:05 PM (UTC+0)">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/amritoo"><img src="https://avatars.githubusercontent.com/u/45586379?v=4&s=24" alt="amritoo" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zenithnovels.com/" target="_blank">http://zenithnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/z/zenithnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://88tangeatdrinkread.wordpress.com/" target="_blank">https://88tangeatdrinkread.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/8/88tang.py" title="01 April 2026 05:15:05 PM (UTC+0)">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovel.org/" target="_blank">https://allnovel.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/allnovel.py" title="22 March 2026 09:34:05 AM (UTC+0)">49</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovelfull.com/" target="_blank">https://allnovelfull.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/allnovelfull.py" title="02 September 2025 06:36:20 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://allnovelfull.net/" target="_blank">https://allnovelfull.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/allnovelfull.py" title="02 September 2025 06:36:20 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://americanfaux.com/" target="_blank">https://americanfaux.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/americanfaux.py" title="01 April 2026 05:15:05 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ancientheartloss.wordpress.com/" target="_blank">https://ancientheartloss.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/ancientheartloss.py" title="01 April 2026 05:15:05 PM (UTC+0)">77</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://api.babelnovel.com/" target="_blank">https://api.babelnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/babelnovel.py" title="13 May 2026 11:40:54 AM (UTC+0)">35</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://aquareader.net/" target="_blank">https://aquareader.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/aquamanga.py" title="13 June 2026 10:10:06 PM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://aquareader.org/" target="_blank">https://aquareader.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/aquamanga.py" title="13 June 2026 10:10:06 PM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://arcanetranslations.com/" target="_blank">https://arcanetranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/arcanetranslations.py" title="22 March 2026 09:34:05 AM (UTC+0)">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://asurascans.com/" target="_blank">https://asurascans.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/asurascans.py" title="01 August 2026 07:51:28 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://automtl.wordpress.com/" target="_blank">https://automtl.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/automtl.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://babelnovel.com/" target="_blank">https://babelnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/babelnovel.py" title="13 May 2026 11:40:54 AM (UTC+0)">35</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bakapervert.wordpress.com/" target="_blank">https://bakapervert.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bakapervert.py" title="01 April 2026 05:15:05 PM (UTC+0)">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://batotwo.com/" target="_blank">https://batotwo.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://battwo.com/" target="_blank">https://battwo.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bednovel.com/" target="_blank">https://bednovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bednovel.py" title="02 April 2026 04:44:15 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://booknet.com/" target="_blank">https://booknet.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/booknet.py" title="29 July 2026 07:15:28 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://chrysanthemumgarden.com/" target="_blank">https://chrysanthemumgarden.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/chrysanthemumgarden.py" title="01 April 2026 05:15:05 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ckandawrites.online/" target="_blank">https://ckandawrites.online/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/ckandawrites.online.py" title="01 August 2026 08:21:48 PM (UTC+0)">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://coffeemanga.io/" target="_blank">https://coffeemanga.io/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/coffeemanga.py" title="06 April 2026 06:15:39 AM (UTC+0)">22</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://comrademao.com/" target="_blank">https://comrademao.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/fu_kemao.py" title="13 May 2026 11:40:54 AM (UTC+0)">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://creativenovels.com/" target="_blank">https://creativenovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/creativenovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">37</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://crescentmoon.blog/" target="_blank">https://crescentmoon.blog/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/crescentmoon.py" title="01 April 2026 05:15:05 PM (UTC+0)">62</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://daotranslate.com/" target="_blank">https://daotranslate.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/daotranslate.py" title="23 July 2026 05:56:51 PM (UTC+0)">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://daotranslate.us/" target="_blank">https://daotranslate.us/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/daotranslate.py" title="23 July 2026 05:56:51 PM (UTC+0)">24</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://demontranslations.com/" target="_blank">https://demontranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/demontrans.py" title="06 April 2026 06:15:39 AM (UTC+0)">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dmtranslationscn.com/" target="_blank">https://dmtranslationscn.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dmtrans.py" title="01 April 2026 05:15:05 PM (UTC+0)">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dobelyuwai.wordpress.com/" target="_blank">https://dobelyuwai.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dobelyuwai.py" title="06 April 2026 06:15:39 AM (UTC+0)">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dobytranslations.com/" target="_blank">https://dobytranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dobytranslations.py" title="01 August 2026 08:21:48 PM (UTC+0)">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dragontea.ink/" target="_blank">https://dragontea.ink/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dragon_tea.py" title="01 April 2026 05:15:05 PM (UTC+0)">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dreamy-translations.com/" target="_blank">https://dreamy-translations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dreamytranslations.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://dto.to/" target="_blank">https://dto.to/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://dummynovels.com/" target="_blank">https://dummynovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/dummynovels.py" title="02 April 2026 04:44:44 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://duskblossoms.com/" target="_blank">https://duskblossoms.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/duskblossoms.py" title="01 August 2026 04:14:09 PM (UTC+0)">77</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ebotnovel.com/" target="_blank">https://ebotnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/e/ebotnovel.py" title="23 July 2024 06:12:46 PM (UTC+0)">2</a></td>
<td></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://exiledrebelsscanlations.com/" target="_blank">https://exiledrebelsscanlations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/e/exiledrebels.py" title="01 April 2026 05:15:05 PM (UTC+0)">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://f-w-o.com/" target="_blank">https://f-w-o.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fantasyworldonline.py" title="06 April 2026 06:15:39 AM (UTC+0)">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://faqwiki.xyz/" target="_blank">https://faqwiki.xyz/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/faqwiki.py" title="01 August 2026 11:44:02 AM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fenrirealm.com/" target="_blank">https://fenrirealm.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fenrirealm.py" title="26 April 2026 08:18:39 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://freemanga.me/" target="_blank">https://freemanga.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/freemanga.py" title="06 April 2026 06:15:39 AM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://freewebnovel.com/" target="_blank">https://freewebnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/freewebnovel.py" title="28 June 2026 10:28:31 AM (UTC+0)">38</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://genesistls.com/" target="_blank">https://genesistls.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/g/genesistls.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://gravitytales.com/" target="_blank">https://gravitytales.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/g/gravitytales.py" title="01 August 2026 12:46:19 PM (UTC+0)">22</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hiraethtranslation.com/" target="_blank">https://hiraethtranslation.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/h/hiraethtranslation.py" title="01 August 2026 07:51:28 PM (UTC+0)">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://home.novel-gate.com/" target="_blank">https://home.novel-gate.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelgate.py" title="03 April 2026 06:55:06 PM (UTC+0)">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hostednovel.com/" target="_blank">https://hostednovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/h/hostednovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://hto.to/" target="_blank">https://hto.to/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hui3r.wordpress.com/" target="_blank">https://hui3r.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/h/hui3r.py" title="06 April 2026 06:15:39 AM (UTC+0)">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://hyacinthbloom.com/" target="_blank">https://hyacinthbloom.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/h/hyacinthbloom.py" title="01 August 2026 08:21:48 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://inadequatetranslations.wordpress.com/" target="_blank">https://inadequatetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/inadequatetrans.py" title="01 April 2026 05:15:05 PM (UTC+0)">74</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://infinitenoveltranslations.net/" target="_blank">https://infinitenoveltranslations.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/infinitetrans.py" title="01 April 2026 05:15:05 PM (UTC+0)">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://isotls.com/" target="_blank">https://isotls.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/isotls.py" title="01 April 2026 05:15:05 PM (UTC+0)">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jobnib.com/" target="_blank">https://jobnib.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/j/jobnib.py" title="01 August 2026 07:51:28 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jpmtl.com/" target="_blank">https://jpmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/j/jpmtl.py" title="06 April 2026 06:15:39 AM (UTC+0)">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jrnovels.com/" target="_blank">https://jrnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/j/jrnovels.py" title="02 August 2026 09:22:09 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://justatranslatortranslations.com/" target="_blank">https://justatranslatortranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/j/justatrans.py" title="06 April 2026 06:15:39 AM (UTC+0)">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://katreadingcafe.com/" target="_blank">https://katreadingcafe.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/k/katreadingcafe.py" title="23 July 2026 05:56:51 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://kinkytranslations.com/" target="_blank">https://kinkytranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/k/kinkytranslations.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://kissmanga.in/" target="_blank">https://kissmanga.in/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/k/kissmanga.py" title="06 April 2026 06:15:39 AM (UTC+0)">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://knoxt.space/" target="_blank">https://knoxt.space/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/k/knoxt.py" title="01 August 2026 10:22:05 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lazybirdtranslations.wordpress.com/" target="_blank">https://lazybirdtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/ladybirdtrans.py" title="06 April 2026 06:15:39 AM (UTC+0)">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lazygirltranslations.com/" target="_blank">https://lazygirltranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lazygirltranslations.py" title="02 April 2026 04:44:44 PM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://leafstudio.site/" target="_blank">https://leafstudio.site/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/leafstudio.py" title="23 July 2026 05:56:51 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lemontreetranslations.wordpress.com/" target="_blank">https://lemontreetranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lemontree.py" title="01 April 2026 05:15:05 PM (UTC+0)">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://librarynovel.com/" target="_blank">https://librarynovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/librarynovel.py" title="02 April 2026 04:44:44 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://libread.com/" target="_blank">https://libread.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/libread_com.py" title="02 April 2026 04:44:15 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://libread.org/" target="_blank">https://libread.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/libread_org.py" title="02 April 2026 04:44:15 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovel.world/" target="_blank">https://lightnovel.world/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelworld.py" title="01 April 2026 05:15:05 PM (UTC+0)">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelheaven.com/" target="_blank">https://lightnovelheaven.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelheaven.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelpub.me/" target="_blank">https://lightnovelpub.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novellive.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelpub.org/" target="_blank">https://lightnovelpub.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelpuborg.py" title="13 June 2026 09:37:36 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelreader.me/" target="_blank">https://lightnovelreader.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelreader.py" title="02 April 2026 04:44:44 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovels.live/" target="_blank">https://lightnovels.live/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelme.py" title="09 May 2026 06:08:01 PM (UTC+0)">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelstranslations.com/" target="_blank">https://lightnovelstranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovetrans.py" title="30 June 2026 06:21:47 AM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnmtl.com/" target="_blank">https://lnmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lnmtl.py" title="12 June 2026 08:44:54 PM (UTC+0)">106</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lnreader.org/" target="_blank">https://lnreader.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelreader.py" title="02 April 2026 04:44:44 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.readlightnovel.cc/" target="_blank">https://m.readlightnovel.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelcc.py" title="02 April 2026 04:44:44 PM (UTC+0)">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.webnovel.com/" target="_blank">https://m.webnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webnovel.py" title="30 July 2026 06:09:12 PM (UTC+0)">103</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangabuddy.com/" target="_blank">https://mangabuddy.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangabuddy.py" title="02 April 2026 04:44:44 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangarosie.love/" target="_blank">https://mangarosie.love/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangarosie.py" title="06 April 2026 06:15:39 AM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangarosie.me/" target="_blank">https://mangarosie.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangarosie.py" title="06 April 2026 06:15:39 AM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mangatoon.mobi/" target="_blank">https://mangatoon.mobi/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangatoon.py" title="02 April 2026 04:44:44 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mangatx.com/" target="_blank">https://mangatx.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangatx.py" title="02 April 2026 04:44:44 PM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://manhuaplus.online/" target="_blank">https://manhuaplus.online/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/manhuaplus.py" title="06 April 2026 06:15:39 AM (UTC+0)">22</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://maplesan9.wordpress.com/" target="_blank">https://maplesan9.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/maplesantl.py" title="02 August 2026 09:22:09 AM (UTC+0)">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://maplesantl.com/" target="_blank">https://maplesantl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/maplesantl.py" title="02 August 2026 09:22:09 AM (UTC+0)">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://miraslation.net/" target="_blank">https://miraslation.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/miraslation.py" title="01 April 2026 05:15:05 PM (UTC+0)">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://mto.to/" target="_blank">https://mto.to/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mydramanovel.com/" target="_blank">https://mydramanovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mydramanovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://mysticalmerries.com/" target="_blank">https://mysticalmerries.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mysticalmerries.py" title="01 April 2026 05:15:05 PM (UTC+0)">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noblemtl.com/" target="_blank">https://noblemtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/noblemtl.py" title="10 October 2022 04:30:09 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel-bin.com/" target="_blank">https://novel-bin.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novel-bin.py" title="23 July 2026 05:56:51 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel-bin.net/" target="_blank">https://novel-bin.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novel-bin.net.py" title="23 July 2026 05:56:51 PM (UTC+0)">3</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novel27.com/" target="_blank">https://novel27.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novel27.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelarrow.com/" target="_blank">https://novelarrow.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelarrow.py" title="23 July 2026 05:56:51 PM (UTC+0)">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbin.net/" target="_blank">https://novelbin.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelbin.net.py" title="29 November 2022 03:01:01 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbuddy.com/" target="_blank">https://novelbuddy.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelbuddy.py" title="01 August 2026 07:51:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbuddy.io/" target="_blank">https://novelbuddy.io/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelbuddy.py" title="01 August 2026 07:51:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelbuddy.me/" target="_blank">https://novelbuddy.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelbuddy.py" title="01 August 2026 07:51:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfire.net/" target="_blank">https://novelfire.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfire.py" title="23 July 2026 05:56:51 PM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.com/" target="_blank">https://novelfull.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfull.py" title="26 March 2024 06:17:03 AM (UTC+0)">50</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.me/" target="_blank">https://novelfull.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfullme.py" title="02 April 2026 04:44:44 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfull.net/" target="_blank">https://novelfull.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfull.py" title="26 March 2024 06:17:03 AM (UTC+0)">50</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfulll.com/" target="_blank">https://novelfulll.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelfulll.py" title="02 August 2026 07:16:28 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhard.com/" target="_blank">https://novelhard.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelhard.py" title="06 April 2026 06:15:39 AM (UTC+0)">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelhi.com/" target="_blank">https://novelhi.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelhi.py" title="02 April 2026 04:44:44 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelight.net/" target="_blank">https://novelight.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelight.py" title="29 July 2026 07:15:28 PM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kardigun"><img src="https://avatars.githubusercontent.com/u/193339894?v=4&s=24" alt="kardigun" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novellive.app/" target="_blank">https://novellive.app/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novellive.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novellive.org/" target="_blank">https://novellive.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novellive.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelmao.com/" target="_blank">https://novelmao.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelmao.py" title="02 June 2026 02:48:19 AM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelnextz.com/" target="_blank">https://novelnextz.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelnextz.py" title="01 April 2024 04:04:16 AM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelonlinefree.com/" target="_blank">https://novelonlinefree.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelonlinefree.py" title="06 April 2026 06:15:39 AM (UTC+0)">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelrare.com/" target="_blank">https://novelrare.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelrare.py" title="06 April 2026 06:15:39 AM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novels.pl/" target="_blank">https://novels.pl/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelspl.py" title="02 April 2026 04:44:44 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelsonline.net/" target="_blank">https://novelsonline.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelsonline.py" title="02 June 2026 07:30:14 PM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltrust.com/" target="_blank">https://noveltrust.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novellive.py" title="02 August 2026 06:57:30 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelww.com/" target="_blank">https://novelww.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelww.py" title="06 April 2026 06:15:39 AM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novgo.net/" target="_blank">https://novgo.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/allnovelfull.py" title="02 September 2025 06:36:20 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novlove.com/" target="_blank">https://novlove.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novlove.py" title="30 May 2025 03:42:49 AM (UTC+0)">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://nyx-translation.com/" target="_blank">https://nyx-translation.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/nyxtranslation.py" title="01 April 2026 05:15:05 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://nyxtranslation.home.blog/" target="_blank">https://nyxtranslation.home.blog/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/nyxtranslation.py" title="01 April 2026 05:15:05 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://pandanovel.co/" target="_blank">https://pandanovel.co/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/p/pandanovelco.py" title="30 July 2026 06:09:12 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://pianmanga.com/" target="_blank">https://pianmanga.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/p/pianmanga.py" title="06 April 2026 06:15:39 AM (UTC+0)">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://puretl.com/" target="_blank">https://puretl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/p/puretl.py" title="03 April 2026 06:55:06 PM (UTC+0)">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://r18novel.com/" target="_blank">https://r18novel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/r18novel.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobes.net/" target="_blank">https://ranobes.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/ranobes.py" title="02 June 2026 07:30:14 PM (UTC+0)">36</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobes.top/" target="_blank">https://ranobes.top/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/ranobes.py" title="02 June 2026 07:30:14 PM (UTC+0)">36</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://re-library.com/" target="_blank">https://re-library.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/relibrary.py" title="23 July 2026 05:56:51 PM (UTC+0)">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovel.me/" target="_blank">https://readlightnovel.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelorg.py" title="01 April 2026 05:15:05 PM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readlightnovel.today/" target="_blank">https://readlightnovel.today/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelorg.py" title="01 April 2026 05:15:05 PM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readmtl.com/" target="_blank">https://readmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readmtl.py" title="10 October 2022 07:53:33 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readnovelfull.com/" target="_blank">https://readnovelfull.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readnovelfull.py" title="04 October 2022 12:43:55 PM (UTC+0)">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readonlinenovels.com/" target="_blank">https://readonlinenovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readonlinenovels.py" title="01 April 2026 05:15:05 PM (UTC+0)">70</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/amritoo"><img src="https://avatars.githubusercontent.com/u/45586379?v=4&s=24" alt="amritoo" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://readwebnovels.net/" target="_blank">https://readwebnovels.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readwebnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://reaperscans.com/" target="_blank">https://reaperscans.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/reaperscans.py" title="23 July 2026 05:56:51 PM (UTC+0)">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://requiemtls.com/" target="_blank">https://requiemtls.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/requiemtls.py" title="23 July 2026 05:56:51 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://revengernovel.com/" target="_blank">https://revengernovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/revengernovel.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnoob.wordpress.com/" target="_blank">https://rpgnoob.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/rpgnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rpgnovels.com/" target="_blank">https://rpgnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/rpgnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://rubymaybetranslations.com/" target="_blank">https://rubymaybetranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/rubymaybetranslations.py" title="02 August 2026 08:39:54 AM (UTC+0)">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://secondlifetranslations.com/" target="_blank">https://secondlifetranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/secondlifetranslations.py" title="01 April 2026 05:15:05 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://shalvationtranslations.wordpress.com/" target="_blank">https://shalvationtranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/shalvation.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://shanghaifantasy.com/" target="_blank">https://shanghaifantasy.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/shanghaifantasy.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://skydemonorder.com/" target="_blank">https://skydemonorder.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/skydemonorder.py" title="26 April 2026 08:19:14 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sleepytranslations.com/" target="_blank">https://sleepytranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/sleepytrans.py" title="06 April 2026 06:15:39 AM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://smnovels.com/" target="_blank">https://smnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/smnovels.py" title="01 April 2026 05:15:05 PM (UTC+0)">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://snowycodex.com/" target="_blank">https://snowycodex.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/snowycodex.py" title="02 April 2026 04:44:44 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://sonicmtl.com/" target="_blank">https://sonicmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/sonicmtl.py" title="22 March 2026 09:34:05 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://stabbingwithasyringe.home.blog/" target="_blank">https://stabbingwithasyringe.home.blog/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/stabbingwithasyringe.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tigertranslations.org/" target="_blank">https://tigertranslations.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/tigertranslations.py" title="06 April 2026 06:15:39 AM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tocqidianunderground.blogspot.com/" target="_blank">https://tocqidianunderground.blogspot.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/q/qidianunderground.py" title="23 July 2026 05:56:51 PM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tomotranslations.com/" target="_blank">https://tomotranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/tomotrans.py" title="02 April 2026 04:44:44 PM (UTC+0)">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://toonily.com/" target="_blank">https://toonily.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/toonily.py" title="02 April 2026 04:44:44 PM (UTC+0)">82</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://translatinotaku.net/" target="_blank">https://translatinotaku.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/translatinotaku.py" title="01 August 2026 07:51:28 PM (UTC+0)">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vipnovel.com/" target="_blank">https://vipnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/v/vipnovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://vistranslations.wordpress.com/" target="_blank">https://vistranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/v/vistrans.py" title="06 April 2026 06:15:39 AM (UTC+0)">76</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wanderinginn.com/" target="_blank">https://wanderinginn.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wanderinginn.py" title="06 April 2026 06:15:39 AM (UTC+0)">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnovelonline.com/" target="_blank">https://webnovelonline.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webnovelonlinecom.py" title="30 July 2026 05:51:36 PM (UTC+0)">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://webnoveltranslations.com/" target="_blank">https://webnoveltranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webnoveltranslations.py" title="01 August 2026 07:51:28 PM (UTC+0)">78</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://whatsawhizzerwebnovels.com/" target="_blank">https://whatsawhizzerwebnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/whatsawhizzerwebnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://whitemoonlightnovels.com/" target="_blank">https://whitemoonlightnovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/whitemoonlightnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wondernovels.com/" target="_blank">https://wondernovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wondernovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://woopread.com/" target="_blank">https://woopread.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/woopread.py" title="02 April 2026 04:44:44 PM (UTC+0)">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordexcerpt.com/" target="_blank">https://wordexcerpt.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wordexcerpt.py" title="30 July 2026 05:51:36 PM (UTC+0)">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wordrain69.com/" target="_blank">https://wordrain69.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wordrain.py" title="13 June 2026 07:28:32 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://wto.to/" target="_blank">https://wto.to/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/b/bato.py" title="01 August 2026 04:14:09 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wujizun.com/" target="_blank">https://wujizun.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wujizun.py" title="06 April 2026 06:15:39 AM (UTC+0)">79</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxia.city/" target="_blank">https://wuxia.city/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiacity.py" title="02 April 2026 04:44:44 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxia.click/" target="_blank">https://wuxia.click/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaclick.py" title="06 April 2026 06:15:39 AM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.name/" target="_blank">https://wuxiaworld.name/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaworldio.py" title="01 April 2026 05:15:05 PM (UTC+0)">28</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.online/" target="_blank">https://wuxiaworld.online/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaonline.py" title="06 April 2026 06:15:39 AM (UTC+0)">33</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wuxiaworld.site/" target="_blank">https://wuxiaworld.site/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaworldsite.py" title="06 April 2026 06:15:39 AM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.allnovel.org/" target="_blank">https://www.allnovel.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/allnovel.py" title="22 March 2026 09:34:05 AM (UTC+0)">49</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.asianhobbyist.com/" target="_blank">https://www.asianhobbyist.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/asianhobbyist.py" title="01 April 2026 05:15:05 PM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.asianovel.net/" target="_blank">https://www.asianovel.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/asianovel_net.py" title="23 July 2026 05:56:51 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kardigun"><img src="https://avatars.githubusercontent.com/u/193339894?v=4&s=24" alt="kardigun" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.chereads.com/" target="_blank">https://www.chereads.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/chereads.py" title="23 July 2026 06:59:30 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.chickengege.org/" target="_blank">https://www.chickengege.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/c/chickengege.py" title="03 April 2026 06:55:06 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.divinedaolibrary.com/" target="_blank">https://www.divinedaolibrary.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/d/divinedaolibrary.py" title="06 April 2026 06:15:39 AM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.f-w-o.com/" target="_blank">https://www.f-w-o.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fantasyworldonline.py" title="06 April 2026 06:15:39 AM (UTC+0)">73</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fanfiction.net/" target="_blank">https://www.fanfiction.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fanfiction.py" title="06 April 2026 06:15:39 AM (UTC+0)">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fanmtl.com/" target="_blank">https://www.fanmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fanmtl.py" title="01 August 2026 07:51:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fansmtl.com/" target="_blank">https://www.fansmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fanmtl.py" title="01 August 2026 07:51:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fictionpress.com/" target="_blank">https://www.fictionpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fictionpress.py" title="06 April 2026 06:15:39 AM (UTC+0)">20</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.flying-lines.com/" target="_blank">https://www.flying-lines.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/flyinglines.py" title="13 May 2026 11:40:54 AM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.foxteller.com/" target="_blank">https://www.foxteller.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/foxteller.py" title="02 April 2026 04:44:44 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.freelightnovel.com/" target="_blank">https://www.freelightnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/freelightnovel.py" title="01 April 2026 05:15:05 PM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fringecapybara.com/" target="_blank">https://www.fringecapybara.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fringecapybara.py" title="01 April 2026 05:15:05 PM (UTC+0)">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.fuyuneko.org/" target="_blank">https://www.fuyuneko.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/f/fuyuneko.py" title="01 April 2026 05:15:05 PM (UTC+0)">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.inkitt.com/" target="_blank">https://www.inkitt.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/inkitt.py" title="02 April 2026 04:44:44 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.isotls.com/" target="_blank">https://www.isotls.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/i/isotls.py" title="01 April 2026 05:15:05 PM (UTC+0)">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.kitenovel.com/" target="_blank">https://www.kitenovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/k/kitenovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelpub.org/" target="_blank">https://www.lightnovelpub.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelpuborg.py" title="13 June 2026 09:37:36 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelreader.me/" target="_blank">https://www.lightnovelreader.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelreader.py" title="02 April 2026 04:44:44 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lightnovelworld.com/" target="_blank">https://www.lightnovelworld.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelworld.com.py" title="10 December 2022 10:50:11 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.literotica.com/" target="_blank">https://www.literotica.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/literotica.py" title="23 July 2026 05:56:51 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.lnreader.org/" target="_blank">https://www.lnreader.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/l/lightnovelreader.py" title="02 April 2026 04:44:44 PM (UTC+0)">21</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.machineslicedbread.xyz/" target="_blank">https://www.machineslicedbread.xyz/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/machineslicedbread.py" title="02 August 2026 07:16:28 AM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.mangaread.org/" target="_blank">https://www.mangaread.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mangaread.py" title="06 April 2026 06:15:39 AM (UTC+0)">81</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.meganovel.com/" target="_blank">https://www.meganovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/meganovel.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.miraslation.net/" target="_blank">https://www.miraslation.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/miraslation.py" title="01 April 2026 05:15:05 PM (UTC+0)">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mvlempyr.com/" target="_blank">https://www.mvlempyr.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mvlempyr.py" title="01 August 2026 07:51:28 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.mvlempyr.io/" target="_blank">https://www.mvlempyr.io/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/m/mvlempyr.py" title="01 August 2026 07:51:28 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.nobadnovel.com/" target="_blank">https://www.nobadnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/nobadnovel.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.novelcool.com/" target="_blank">https://www.novelcool.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelcool.py" title="02 June 2026 07:30:14 PM (UTC+0)">40</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelhall.com/" target="_blank">https://www.novelhall.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelhall.py" title="01 April 2026 05:15:05 PM (UTC+0)">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelmtl.com/" target="_blank">https://www.novelmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelmtl.py" title="06 January 2025 04:08:51 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelpassion.com/" target="_blank">https://www.novelpassion.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelpassion.py" title="01 April 2026 05:15:05 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelpub.com/" target="_blank">https://www.novelpub.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelpub.py" title="10 December 2022 10:50:11 PM (UTC+0)">18</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/Galunid"><img src="https://avatars.githubusercontent.com/u/10298730?v=4&s=24" alt="Galunid" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novels.pl/" target="_blank">https://www.novels.pl/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelspl.py" title="02 April 2026 04:44:44 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novelupdates.cc/" target="_blank">https://www.novelupdates.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/n/novelupdatescc.py" title="02 April 2026 04:44:44 PM (UTC+0)">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.oppatranslations.com/" target="_blank">https://www.oppatranslations.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/o/oppatrans.py" title="01 April 2026 05:15:05 PM (UTC+0)">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.pandamanga.xyz/" target="_blank">https://www.pandamanga.xyz/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/p/pandamanga.py" title="10 October 2022 04:20:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.cc/" target="_blank">https://www.readlightnovel.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelcc.py" title="02 April 2026 04:44:44 PM (UTC+0)">17</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.me/" target="_blank">https://www.readlightnovel.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelorg.py" title="01 April 2026 05:15:05 PM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readlightnovel.today/" target="_blank">https://www.readlightnovel.today/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readlightnovelorg.py" title="01 April 2026 05:15:05 PM (UTC+0)">80</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.readwn.com/" target="_blank">https://www.readwn.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/readwn.py" title="22 March 2026 09:34:05 AM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/mesmerlord"><img src="https://avatars.githubusercontent.com/u/76161333?v=4&s=24" alt="mesmerlord" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.royalroad.com/" target="_blank">https://www.royalroad.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/r/royalroad.py" title="23 July 2026 05:56:51 PM (UTC+0)">94</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a> <a href="https://github.com/needKVAS"><img src="https://avatars.githubusercontent.com/u/43537033?v=4&s=24" alt="needKVAS" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.scribblehub.com/" target="_blank">https://www.scribblehub.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/scribblehub.py" title="02 June 2026 07:30:14 PM (UTC+0)">50</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.sonicmtl.com/" target="_blank">https://www.sonicmtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/s/sonicmtl.py" title="22 March 2026 09:34:05 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.tapread.com/" target="_blank">https://www.tapread.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/tapread.py" title="01 April 2026 05:15:05 PM (UTC+0)">60</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.teanovel.com/" target="_blank">https://www.teanovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/t/teanovel.py" title="23 July 2026 06:59:30 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.virlyce.com/" target="_blank">https://www.virlyce.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/v/virlyce.py" title="01 April 2026 05:15:05 PM (UTC+0)">69</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.volarenovels.com/" target="_blank">https://www.volarenovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/v/volarenovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">66</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovel.com/" target="_blank">https://www.webnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webnovel.py" title="30 July 2026 06:09:12 PM (UTC+0)">103</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovelpub.com/" target="_blank">https://www.webnovelpub.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webnovelpub.py" title="06 January 2025 04:08:51 PM (UTC+0)">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa">🖼️</span></td>
<td><a href="https://www.webtoons.com/" target="_blank">https://www.webtoons.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/webtoon.py" title="02 April 2026 04:44:44 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxia.blog/" target="_blank">https://www.wuxia.blog/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiablog.py" title="06 April 2026 06:15:39 AM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiabox.com/" target="_blank">https://www.wuxiabox.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiabox.py" title="03 November 2024 02:48:34 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxialeague.com/" target="_blank">https://www.wuxialeague.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxialeague.py" title="01 April 2026 05:15:05 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiamtl.com/" target="_blank">https://www.wuxiamtl.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiamtl.py" title="22 March 2026 09:34:05 AM (UTC+0)">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiapub.com/" target="_blank">https://www.wuxiapub.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiapub.py" title="22 March 2026 09:34:05 AM (UTC+0)">4</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/zerty"><img src="https://avatars.githubusercontent.com/u/4232921?v=4&s=24" alt="zerty" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiasky.net/" target="_blank">https://www.wuxiasky.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/a/asianovel_net.py" title="23 July 2026 05:56:51 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/kardigun"><img src="https://avatars.githubusercontent.com/u/193339894?v=4&s=24" alt="kardigun" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaspot.com/" target="_blank">https://www.wuxiaspot.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaspot.py" title="06 January 2025 04:08:51 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.wuxiaworld.com/" target="_blank">https://www.wuxiaworld.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/w/wuxiaworldcom.py" title="30 July 2026 06:09:12 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://zetrotranslation.com/" target="_blank">https://zetrotranslation.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/en/z/zetrotranslation.py" title="06 April 2026 06:15:39 AM (UTC+0)">86</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/kuwoyuki"><img src="https://avatars.githubusercontent.com/u/51709703?v=4&s=24" alt="kuwoyuki" height="24"/></a></td>
</tr>
</tbody>
</table>


### `es` Spanish; Castilian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://cclawtranslations.home.blog/" target="_blank">https://cclawtranslations.home.blog/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/es/domentranslations.py" title="06 April 2026 06:15:39 AM (UTC+0)">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://domentranslations.wordpress.com/" target="_blank">https://domentranslations.wordpress.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/es/domentranslations.py" title="06 April 2026 06:15:39 AM (UTC+0)">75</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelasligeras.net/" target="_blank">https://novelasligeras.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/es/novelasligeras.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.skynovels.net/" target="_blank">https://www.skynovels.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/es/skynovels.py" title="01 August 2026 10:22:05 PM (UTC+0)">1</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `fr` French

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://chireads.com/" target="_blank">https://chireads.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/fr/chireads.py" title="31 July 2026 04:21:17 AM (UTC+0)">14</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://lightnovelfr.com/" target="_blank">https://lightnovelfr.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/fr/lightnovelfr.py" title="01 August 2026 08:21:48 PM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveldeglace.com/" target="_blank">https://noveldeglace.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/fr/noveldeglace.py" title="02 April 2026 04:44:44 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelfrance.fr/" target="_blank">https://novelfrance.fr/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/fr/novelfrance.py" title="17 May 2026 09:25:25 AM (UTC+0)">1</a></td>
<td></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://xiaowaz.fr/" target="_blank">https://xiaowaz.fr/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/fr/xiaowaz.py" title="06 April 2026 06:15:39 AM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
</tbody>
</table>


### `id` Indonesian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zhi-end.blogspot.co.id/" target="_blank">http://zhi-end.blogspot.co.id/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/zhiend.py" title="02 April 2026 04:44:44 PM (UTC+0)">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="http://zhi-end.blogspot.com/" target="_blank">http://zhi-end.blogspot.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/zhiend.py" title="02 April 2026 04:44:44 PM (UTC+0)">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://darktranslation.com/" target="_blank">https://darktranslation.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/darktrans.py" title="01 April 2026 05:15:05 PM (UTC+0)">71</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fuyu-novel.my.id/" target="_blank">https://fuyu-novel.my.id/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/fuyunovel.py" title="01 August 2026 08:21:48 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://grensia.blogspot.com/" target="_blank">https://grensia.blogspot.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/grensia_blogspot.py" title="01 April 2026 05:15:05 PM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://indowebnovel.id/" target="_blank">https://indowebnovel.id/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/indowebnovel.py" title="02 April 2026 04:44:44 PM (UTC+0)">65</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://meionovel.id/" target="_blank">https://meionovel.id/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/meionovel.py" title="02 April 2026 04:44:44 PM (UTC+0)">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://meionovels.com/" target="_blank">https://meionovels.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/meionovel.py" title="02 April 2026 04:44:44 PM (UTC+0)">68</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelgo.id/" target="_blank">https://novelgo.id/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/novelgo.py" title="02 April 2026 04:44:44 PM (UTC+0)">19</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelringan.com/" target="_blank">https://novelringan.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/novelringan.py" title="06 April 2026 06:15:39 AM (UTC+0)">63</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://noveltoon.mobi/" target="_blank">https://noveltoon.mobi/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/noveltoon.py" title="06 April 2026 06:15:39 AM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://wbnovel.com/" target="_blank">https://wbnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/wbnovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">67</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.webnovelover.com/" target="_blank">https://www.webnovelover.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/webnovelover.py" title="06 April 2026 06:15:39 AM (UTC+0)">72</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.worldnovel.online/" target="_blank">https://www.worldnovel.online/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/id/worldnovelonline.py" title="01 April 2026 05:15:05 PM (UTC+0)">84</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/yudilee"><img src="https://avatars.githubusercontent.com/u/7065691?v=4&s=24" alt="yudilee" height="24"/></a></td>
</tr>
</tbody>
</table>


### `ja` Japanese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ncode.syosetu.com/" target="_blank">https://ncode.syosetu.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ja/syosetu.py" title="23 July 2026 06:59:30 PM (UTC+0)">27</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://syosetu.org/" target="_blank">https://syosetu.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ja/syosetuorg.py" title="23 July 2026 06:59:30 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `pt` Portuguese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://blnovels.net/" target="_blank">https://blnovels.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/blnovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://centralnovel.com/" target="_blank">https://centralnovel.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/centralnovel.py" title="23 July 2026 05:56:51 PM (UTC+0)">15</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://illusia.com.br/" target="_blank">https://illusia.com.br/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/illusia.py" title="02 April 2026 04:44:44 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://novelmania.com.br/" target="_blank">https://novelmania.com.br/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/novelmania_com_br.py" title="02 June 2026 07:30:14 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://phoenixnovels.com.br/" target="_blank">https://phoenixnovels.com.br/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/phoenixnovels.py" title="02 April 2026 04:44:44 PM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching">🔍</span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tsundoku.com.br/" target="_blank">https://tsundoku.com.br/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/pt/tsundoku.py" title="01 August 2026 08:21:48 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a></td>
</tr>
</tbody>
</table>


### `ru` Russian

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://author.today/" target="_blank">https://author.today/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/authortoday.py" title="23 July 2026 05:56:51 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://bookhamster.ru/" target="_blank">https://bookhamster.ru/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ifreedom.py" title="06 April 2026 06:15:39 AM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://funbook.su/" target="_blank">https://funbook.su/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ifreedom.py" title="06 April 2026 06:15:39 AM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ifreedom.su/" target="_blank">https://ifreedom.su/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ifreedom.py" title="06 April 2026 06:15:39 AM (UTC+0)">8</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://jaomix.ru/" target="_blank">https://jaomix.ru/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/jaomix.py" title="23 July 2026 05:56:51 PM (UTC+0)">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/idMysteries"><img src="https://avatars.githubusercontent.com/u/11484976?v=4&s=24" alt="idMysteries" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/watzeedzad"><img src="https://avatars.githubusercontent.com/u/16551821?v=4&s=24" alt="watzeedzad" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://labnovel.ru/" target="_blank">https://labnovel.ru/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/labnovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://litnet.com/" target="_blank">https://litnet.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/litnet.py" title="29 July 2026 07:15:28 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobe-novels.ru/" target="_blank">https://ranobe-novels.ru/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ranobenovel.py" title="06 April 2026 06:15:39 AM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobelib.me/" target="_blank">https://ranobelib.me/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ranobelib.py" title="23 July 2026 05:56:51 PM (UTC+0)">13</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/needKVAS"><img src="https://avatars.githubusercontent.com/u/43537033?v=4&s=24" alt="needKVAS" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ranobes.com/" target="_blank">https://ranobes.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/ranobes.py" title="02 August 2026 12:27:51 AM (UTC+0)">2</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://renovels.org/" target="_blank">https://renovels.org/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/renovels.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tl.rulate.ru/" target="_blank">https://tl.rulate.ru/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/ru/rulate.py" title="01 April 2026 05:15:05 PM (UTC+0)">11</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a> <a href="https://github.com/needKVAS"><img src="https://avatars.githubusercontent.com/u/43537033?v=4&s=24" alt="needKVAS" height="24"/></a></td>
</tr>
</tbody>
</table>


### `tr` Turkish

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://fenrirscans.com/" target="_blank">https://fenrirscans.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/tr/fenrirscan.py" title="31 July 2026 04:21:17 AM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `vi` Vietnamese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://docln.net/" target="_blank">https://docln.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/vi/lnhakone.py" title="23 July 2026 05:56:51 PM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ln.hako.vn/" target="_blank">https://ln.hako.vn/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/vi/lnhakone.py" title="23 July 2026 05:56:51 PM (UTC+0)">16</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyenfull.today/" target="_blank">https://truyenfull.today/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/vi/truenfull.py" title="02 June 2026 11:46:06 AM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations">🤖</span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://truyenfull.vn/" target="_blank">https://truyenfull.vn/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/vi/truenfull.py" title="02 June 2026 11:46:06 AM (UTC+0)">10</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
</tbody>
</table>


### `zh` Chinese

<table>
<tbody>
<tr><th></th>
<th>Source URL</th>
<th>Version</th>
<th>Contributors</th>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://69shuba.cx/" target="_blank">https://69shuba.cx/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/69shuba.cx.py" title="23 July 2026 05:56:51 PM (UTC+0)">32</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/Aeterno8"><img src="https://avatars.githubusercontent.com/u/109911779?v=4&s=24" alt="Aeterno8" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ixdzs8.com/" target="_blank">https://ixdzs8.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ixdzs.py" title="01 April 2026 05:15:05 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://ixdzs8.tw/" target="_blank">https://ixdzs8.tw/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ixdzs.py" title="01 April 2026 05:15:05 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://m.shuhaige.net/" target="_blank">https://m.shuhaige.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/shuhaige.py" title="01 August 2026 10:22:05 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://trxs.cc/" target="_blank">https://trxs.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/trxs.py" title="06 April 2026 06:15:39 AM (UTC+0)">5</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://tw.m.ixdzs.com/" target="_blank">https://tw.m.ixdzs.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ixdzs.py" title="01 April 2026 05:15:05 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.69shu.com/" target="_blank">https://www.69shu.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/69shuba.py" title="01 August 2026 04:14:09 PM (UTC+0)">29</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/Aeterno8"><img src="https://avatars.githubusercontent.com/u/109911779?v=4&s=24" alt="Aeterno8" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.69shuba.com/" target="_blank">https://www.69shuba.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/69shuba.py" title="01 August 2026 04:14:09 PM (UTC+0)">29</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a> <a href="https://github.com/Aeterno8"><img src="https://avatars.githubusercontent.com/u/109911779?v=4&s=24" alt="Aeterno8" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.aixdzs.com/" target="_blank">https://www.aixdzs.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ixdzs.py" title="01 April 2026 05:15:05 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.banxia.cc/" target="_blank">https://www.banxia.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/xbanxia.py" title="01 April 2026 05:15:05 PM (UTC+0)">25</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.bq99.cc/" target="_blank">https://www.bq99.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/shw5.py" title="06 April 2026 06:15:39 AM (UTC+0)">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ddtxt8.cc/" target="_blank">https://www.ddtxt8.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ddxsss.py" title="23 July 2026 05:56:51 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ddxss.cc/" target="_blank">https://www.ddxss.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/ddxsss.py" title="23 July 2026 05:56:51 PM (UTC+0)">12</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.novel543.com/" target="_blank">https://www.novel543.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/novel543.py" title="02 April 2026 04:44:44 PM (UTC+0)">7</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.piaotia.com/" target="_blank">https://www.piaotia.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/piaotian.py" title="29 July 2026 07:15:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.piaotian.com/" target="_blank">https://www.piaotian.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/piaotian.py" title="29 July 2026 07:15:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.powanjuan.cc/" target="_blank">https://www.powanjuan.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/powanjuan.py" title="06 April 2026 06:15:39 AM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.ptwxz.com/" target="_blank">https://www.ptwxz.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/piaotian.py" title="29 July 2026 07:15:28 PM (UTC+0)">9</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/Zokhoi"><img src="https://avatars.githubusercontent.com/u/20432565?v=4&s=24" alt="Zokhoi" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.shuhaige.net/" target="_blank">https://www.shuhaige.net/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/shuhaige.py" title="01 August 2026 10:22:05 PM (UTC+0)">6</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.shw5.cc/" target="_blank">https://www.shw5.cc/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/shw5.py" title="06 April 2026 06:15:39 AM (UTC+0)">23</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/CryZFix"><img src="https://avatars.githubusercontent.com/u/13964422?v=4&s=24" alt="CryZFix" height="24"/></a></td>
</tr>
<tr><td><span title="Contains machine translations"></span><span title="Supports searching"></span><span title="Supports login"></span><span title="Contains manga/manhua/manhwa"></span></td>
<td><a href="https://www.xbanxia.com/" target="_blank">https://www.xbanxia.com/</a></td>
<td><a href="https://github.com/lncrawl/lightnovel-crawler/blob/93c95228618d208ff724c54da5b21b41be216c4f/sources/zh/xbanxia.py" title="01 April 2026 05:15:05 PM (UTC+0)">25</a></td>
<td><a href="https://github.com/dipu-bd"><img src="https://avatars.githubusercontent.com/u/5158124?v=4&s=24" alt="dipu-bd" height="24"/></a> <a href="https://github.com/SirGryphin"><img src="https://avatars.githubusercontent.com/u/36343615?v=4&s=24" alt="SirGryphin" height="24"/></a> <a href="https://github.com/jere344"><img src="https://avatars.githubusercontent.com/u/86294972?v=4&s=24" alt="jere344" height="24"/></a></td>
</tr>
</tbody>
</table>
<!-- auto generated supported sources list -->

</details>

## Rejected sources

<details>
<summary>Click to expand</summary>
<!-- auto generated rejected sources list -->

<table>
<tbody>
<tr><th>Source URL</th>
<th>Rejection Cause</th>
</tr>
<tr><td><a href="http://boxnovel.org/" target="_blank">http://boxnovel.org/</a></td>
<td>No longer operational</td>
</tr>
<tr><td><a href="http://fullnovel.live/" target="_blank">http://fullnovel.live/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="http://lightnovels.me/" target="_blank">http://lightnovels.me/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="http://wnmtl.org/" target="_blank">http://wnmtl.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="http://wspadancewichita.com/" target="_blank">http://wspadancewichita.com/</a></td>
<td>Site closed and moved to https://readnovelfull.com/</td>
</tr>
<tr><td><a href="http://www.fujitranslation.com/" target="_blank">http://www.fujitranslation.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="http://www.hanyunovels.site/" target="_blank">http://www.hanyunovels.site/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="http://www.wnmtl.org/" target="_blank">http://www.wnmtl.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://1stkissnovel.love/" target="_blank">https://1stkissnovel.love/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://1stkissnovel.org/" target="_blank">https://1stkissnovel.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://4scanlation.com/" target="_blank">https://4scanlation.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://69shu.me/" target="_blank">https://69shu.me/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://888novel.com/" target="_blank">https://888novel.com/</a></td>
<td>Domain is for sale</td>
</tr>
<tr><td><a href="https://allnovelxo.com/" target="_blank">https://allnovelxo.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://amnesiactl.com/" target="_blank">https://amnesiactl.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://ancientheartloss.com/" target="_blank">https://ancientheartloss.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://anime-sama.fr/" target="_blank">https://anime-sama.fr/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://anythingnovel.com/" target="_blank">https://anythingnovel.com/</a></td>
<td>The domain is for sale</td>
</tr>
<tr><td><a href="https://aquamanga.com/" target="_blank">https://aquamanga.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://aquamanga.org/" target="_blank">https://aquamanga.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://arangscans.com/" target="_blank">https://arangscans.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://arnovel.me/" target="_blank">https://arnovel.me/</a></td>
<td>Redirects to an ad network</td>
</tr>
<tr><td><a href="https://asadatranslations.com/" target="_blank">https://asadatranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://bato.to/" target="_blank">https://bato.to/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://batocc.com/" target="_blank">https://batocc.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://batotoo.com/" target="_blank">https://batotoo.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://beautymanga.com/" target="_blank">https://beautymanga.com/</a></td>
<td>Domain now hosts an anime blog with no readable manga</td>
</tr>
<tr><td><a href="https://bestlightnovel.com/" target="_blank">https://bestlightnovel.com/</a></td>
<td>Redirects to an affiliate link</td>
</tr>
<tr><td><a href="https://bestmanga.club/" target="_blank">https://bestmanga.club/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://bestoflightnovels.com/" target="_blank">https://bestoflightnovels.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://bonnovel.com/" target="_blank">https://bonnovel.com/</a></td>
<td>Cloudflare Error 1000, the zone's DNS points at a prohibited address</td>
</tr>
<tr><td><a href="https://boxnovel.com/" target="_blank">https://boxnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://boxnovel.online/" target="_blank">https://boxnovel.online/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://boxnovel.org/" target="_blank">https://boxnovel.org/</a></td>
<td>No longer operational</td>
</tr>
<tr><td><a href="https://bronovel.com/" target="_blank">https://bronovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://chapmanganato.com/" target="_blank">https://chapmanganato.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://clicknovel.net/" target="_blank">https://clicknovel.net/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://comiko.net/" target="_blank">https://comiko.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://daonovel.com/" target="_blank">https://daonovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://dsrealmtranslations.com/" target="_blank">https://dsrealmtranslations.com/</a></td>
<td>Domain expired</td>
</tr>
<tr><td><a href="https://earlynovel.net/" target="_blank">https://earlynovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://engnovel.com/" target="_blank">https://engnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://fanstranslations.com/" target="_blank">https://fanstranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://fenrirtranslations.com/" target="_blank">https://fenrirtranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://freefullnovel.com/" target="_blank">https://freefullnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://fsapk.com/" target="_blank">https://fsapk.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://fujitranslation.com/" target="_blank">https://fujitranslation.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://harimanga.com/" target="_blank">https://harimanga.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://hotnovelfull.com/" target="_blank">https://hotnovelfull.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://imperfectcomic.org/" target="_blank">https://imperfectcomic.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://indomtl.com/" target="_blank">https://indomtl.com/</a></td>
<td>Not crawler friendly</td>
</tr>
<tr><td><a href="https://innnovel.com/" target="_blank">https://innnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://innread.com/" target="_blank">https://innread.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://instadoses.com/" target="_blank">https://instadoses.com/</a></td>
<td>Domain is for sale</td>
</tr>
<tr><td><a href="https://isekaiscan.com/" target="_blank">https://isekaiscan.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://isekaiscan.eu/" target="_blank">https://isekaiscan.eu/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://king-manga.com/" target="_blank">https://king-manga.com/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://kiss-novel.com/" target="_blank">https://kiss-novel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://latestnovel.net/" target="_blank">https://latestnovel.net/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://light-novel.online/" target="_blank">https://light-novel.online/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://lightnovel.tv/" target="_blank">https://lightnovel.tv/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://lightnovelbastion.com/" target="_blank">https://lightnovelbastion.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://lightnovelkiss.com/" target="_blank">https://lightnovelkiss.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://lightnovels.me/" target="_blank">https://lightnovels.me/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://lightnovelshub.com/" target="_blank">https://lightnovelshub.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://lightnovelsonl.com/" target="_blank">https://lightnovelsonl.com/</a></td>
<td>Redirects to an emoji site</td>
</tr>
<tr><td><a href="https://listnovel.com/" target="_blank">https://listnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://lnmtlfr.com/" target="_blank">https://lnmtlfr.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://luminarynovels.com/" target="_blank">https://luminarynovels.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://lunarletters.com/" target="_blank">https://lunarletters.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://m.27k.net/" target="_blank">https://m.27k.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://m.wuxiaworld.co/" target="_blank">https://m.wuxiaworld.co/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://manga-tx.com/" target="_blank">https://manga-tx.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mangachill.io/" target="_blank">https://mangachill.io/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mangachill.love/" target="_blank">https://mangachill.love/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mangarockteam.com/" target="_blank">https://mangarockteam.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mangastic.net/" target="_blank">https://mangastic.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mangatoto.com/" target="_blank">https://mangatoto.com/</a></td>
<td>Domain no longer hosts manga or novels</td>
</tr>
<tr><td><a href="https://mangatoto.net/" target="_blank">https://mangatoto.net/</a></td>
<td>Redirects to a gambling site</td>
</tr>
<tr><td><a href="https://mangatoto.org/" target="_blank">https://mangatoto.org/</a></td>
<td>Domain now serves a gambling site</td>
</tr>
<tr><td><a href="https://mangaweebs.in/" target="_blank">https://mangaweebs.in/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://manhwachill.com/" target="_blank">https://manhwachill.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://meownovel.com/" target="_blank">https://meownovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mixednovel.net/" target="_blank">https://mixednovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mltnovels.com/" target="_blank">https://mltnovels.com/</a></td>
<td>Redirects to an ad network</td>
</tr>
<tr><td><a href="https://morenovel.net/" target="_blank">https://morenovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mostnovel.com/" target="_blank">https://mostnovel.com/</a></td>
<td>Redirects to a gambling site</td>
</tr>
<tr><td><a href="https://mtled-novels.com/" target="_blank">https://mtled-novels.com/</a></td>
<td>Domain is expired</td>
</tr>
<tr><td><a href="https://mtlnation.com/" target="_blank">https://mtlnation.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://mtlreader.com/" target="_blank">https://mtlreader.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://myboxnovel.com/" target="_blank">https://myboxnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://myoniyonitranslations.com/" target="_blank">https://myoniyonitranslations.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://myreadingmanga.fit/" target="_blank">https://myreadingmanga.fit/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://newnovel.org/" target="_blank">https://newnovel.org/</a></td>
<td>Redirects to a parked lander</td>
</tr>
<tr><td><a href="https://newsite.kolnovel.com/" target="_blank">https://newsite.kolnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://noobchan.xyz/" target="_blank">https://noobchan.xyz/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novel35.com/" target="_blank">https://novel35.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelasligera.com/" target="_blank">https://novelasligera.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelbin.com/" target="_blank">https://novelbin.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelbin.me/" target="_blank">https://novelbin.me/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelcake.com/" target="_blank">https://novelcake.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelcrush.com/" target="_blank">https://novelcrush.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelfullplus.com/" target="_blank">https://novelfullplus.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelgate.net/" target="_blank">https://novelgate.net/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://novelhulk.com/" target="_blank">https://novelhulk.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelku.id/" target="_blank">https://novelku.id/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelmic.com/" target="_blank">https://novelmic.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelnext.com/" target="_blank">https://novelnext.com/</a></td>
<td>Flagged by Cloudflare as suspected phishing</td>
</tr>
<tr><td><a href="https://novelnext.dramanovels.io/" target="_blank">https://novelnext.dramanovels.io/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelonlinefull.com/" target="_blank">https://novelonlinefull.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelplanet.com/" target="_blank">https://novelplanet.com/</a></td>
<td>Site is closed</td>
</tr>
<tr><td><a href="https://novelraw.blogspot.com/" target="_blank">https://novelraw.blogspot.com/</a></td>
<td>Site closed down</td>
</tr>
<tr><td><a href="https://novelsala.com/" target="_blank">https://novelsala.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelsemperor.com/" target="_blank">https://novelsemperor.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelsite.net/" target="_blank">https://novelsite.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelsrock.com/" target="_blank">https://novelsrock.com/</a></td>
<td>Web server is down</td>
</tr>
<tr><td><a href="https://noveltranslate.com/" target="_blank">https://noveltranslate.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://novelzec.com/" target="_blank">https://novelzec.com/</a></td>
<td>Redirects to a gambling site</td>
</tr>
<tr><td><a href="https://omgnovels.com/" target="_blank">https://omgnovels.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://overabook.com/" target="_blank">https://overabook.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://pandamtl.com/" target="_blank">https://pandamtl.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://pandanovel.org/" target="_blank">https://pandanovel.org/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://pery.info/" target="_blank">https://pery.info/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://raeitranslations.com/" target="_blank">https://raeitranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://randomnovel.com/" target="_blank">https://randomnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://read.asianovel.com/" target="_blank">https://read.asianovel.com/</a></td>
<td>Connection timed out</td>
</tr>
<tr><td><a href="https://readlitenovel.com/" target="_blank">https://readlitenovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://readmanganato.com/" target="_blank">https://readmanganato.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://readnovelz.net/" target="_blank">https://readnovelz.net/</a></td>
<td>Redirects to webnovelonline.net</td>
</tr>
<tr><td><a href="https://reincarnationpalace.com/" target="_blank">https://reincarnationpalace.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://sj.uukanshu.net/" target="_blank">https://sj.uukanshu.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://skynovel.org/" target="_blank">https://skynovel.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://so.27k.net/" target="_blank">https://so.27k.net/</a></td>
<td>Domain registration has expired</td>
</tr>
<tr><td><a href="https://steambunlightnovel.com/" target="_blank">https://steambunlightnovel.com/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://supernovel.net/" target="_blank">https://supernovel.net/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://systemtranslation.com/" target="_blank">https://systemtranslation.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://tamagotl.com/" target="_blank">https://tamagotl.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://tipnovel.com/" target="_blank">https://tipnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://toc.qidianunderground.org/" target="_blank">https://toc.qidianunderground.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://toon69.com/" target="_blank">https://toon69.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://totallytranslations.com/" target="_blank">https://totallytranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://travistranslations.com/" target="_blank">https://travistranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://truyentr.info/" target="_blank">https://truyentr.info/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://tunovelaligera.com/" target="_blank">https://tunovelaligera.com/</a></td>
<td>Broken. Chapters does not load</td>
</tr>
<tr><td><a href="https://tw.27k.net/" target="_blank">https://tw.27k.net/</a></td>
<td>Domain now hosts an unrelated service</td>
</tr>
<tr><td><a href="https://tw.uukanshu.net/" target="_blank">https://tw.uukanshu.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://usefulnovel.com/" target="_blank">https://usefulnovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://veratales.com/" target="_blank">https://veratales.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://viewnovel.net/" target="_blank">https://viewnovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://webnovelindonesia.com/" target="_blank">https://webnovelindonesia.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://webnovelonline.net/" target="_blank">https://webnovelonline.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://wnmtl.org/" target="_blank">https://wnmtl.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://writerupdates.com/" target="_blank">https://writerupdates.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://wuxiaworld.io/" target="_blank">https://wuxiaworld.io/</a></td>
<td>Cloudflare Error 522, can not connect to host</td>
</tr>
<tr><td><a href="https://wuxiaworld.live/" target="_blank">https://wuxiaworld.live/</a></td>
<td>The domain has expired</td>
</tr>
<tr><td><a href="https://wuxiaworldsite.co/" target="_blank">https://wuxiaworldsite.co/</a></td>
<td>No longer provides lightnovels</td>
</tr>
<tr><td><a href="https://www.27k.net/" target="_blank">https://www.27k.net/</a></td>
<td>Domain registration has expired</td>
</tr>
<tr><td><a href="https://www.69shu.pro/" target="_blank">https://www.69shu.pro/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://www.69shuba.pro/" target="_blank">https://www.69shuba.pro/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://www.69xinshu.com/" target="_blank">https://www.69xinshu.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.blackbox-tl.com/" target="_blank">https://www.blackbox-tl.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.box-novel.com/" target="_blank">https://www.box-novel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.centinni.com/" target="_blank">https://www.centinni.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.ceunovel.com/" target="_blank">https://www.ceunovel.com/</a></td>
<td>site is down</td>
</tr>
<tr><td><a href="https://www.daocaorenshuwu.com/" target="_blank">https://www.daocaorenshuwu.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.idqidian.us/" target="_blank">https://www.idqidian.us/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.koreanmtl.online/" target="_blank">https://www.koreanmtl.online/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.lightnovelmeta.com/" target="_blank">https://www.lightnovelmeta.com/</a></td>
<td>Redirects to an ad network</td>
</tr>
<tr><td><a href="https://www.lightnovelpub.com/" target="_blank">https://www.lightnovelpub.com/</a></td>
<td>Platform has been terminated</td>
</tr>
<tr><td><a href="https://www.lreads.com/" target="_blank">https://www.lreads.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.ltnovel.com/" target="_blank">https://www.ltnovel.com/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://www.machine-translation.org/" target="_blank">https://www.machine-translation.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.mangaweebs.in/" target="_blank">https://www.mangaweebs.in/</a></td>
<td>Domain is parked and for sale</td>
</tr>
<tr><td><a href="https://www.mtlnation.com/" target="_blank">https://www.mtlnation.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.mtlreader.com/" target="_blank">https://www.mtlreader.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.neosekaitranslations.com/" target="_blank">https://www.neosekaitranslations.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.newsnovel.net/" target="_blank">https://www.newsnovel.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelall.com/" target="_blank">https://www.novelall.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelhunters.com/" target="_blank">https://www.novelhunters.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelmt.com/" target="_blank">https://www.novelmt.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelmultiverse.com/" target="_blank">https://www.novelmultiverse.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelspread.com/" target="_blank">https://www.novelspread.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.noveluniverse.com/" target="_blank">https://www.noveluniverse.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.novelv.com/" target="_blank">https://www.novelv.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.ornovel.com/" target="_blank">https://www.ornovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.p2wt.com/" target="_blank">https://www.p2wt.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.rebirth.online/" target="_blank">https://www.rebirth.online/</a></td>
<td>Redrects to https://foxteller.com/</td>
</tr>
<tr><td><a href="https://www.shinsori.com/" target="_blank">https://www.shinsori.com/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://www.soxs.cc/" target="_blank">https://www.soxs.cc/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.topmanhua.com/" target="_blank">https://www.topmanhua.com/</a></td>
<td>Redirects to an ad network</td>
</tr>
<tr><td><a href="https://www.translateindo.com/" target="_blank">https://www.translateindo.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.uukanshu.net/" target="_blank">https://www.uukanshu.net/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.webnovelpub.pro/" target="_blank">https://www.webnovelpub.pro/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wnmtl.org/" target="_blank">https://www.wnmtl.org/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiahub.com/" target="_blank">https://www.wuxiahub.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxianovelhub.com/" target="_blank">https://www.wuxianovelhub.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiap.com/" target="_blank">https://www.wuxiap.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiar.com/" target="_blank">https://www.wuxiar.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiau.com/" target="_blank">https://www.wuxiau.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiav.com/" target="_blank">https://www.wuxiav.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiaworld.co/" target="_blank">https://www.wuxiaworld.co/</a></td>
<td>This site can not be reached</td>
</tr>
<tr><td><a href="https://www.wuxiax.com/" target="_blank">https://www.wuxiax.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.wuxiaz.com/" target="_blank">https://www.wuxiaz.com/</a></td>
<td>Redirects to an ad network</td>
</tr>
<tr><td><a href="https://www.xiainovel.com/" target="_blank">https://www.xiainovel.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://www.xnunu.com/" target="_blank">https://www.xnunu.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://yonglibrary.com/" target="_blank">https://yonglibrary.com/</a></td>
<td>Site closed</td>
</tr>
<tr><td><a href="https://yukinovel.id/" target="_blank">https://yukinovel.id/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://yukinovel.me/" target="_blank">https://yukinovel.me/</a></td>
<td>Domain is for sale</td>
</tr>
<tr><td><a href="https://zinmanga.com/" target="_blank">https://zinmanga.com/</a></td>
<td>Site is down</td>
</tr>
<tr><td><a href="https://zinnovel.com/" target="_blank">https://zinnovel.com/</a></td>
<td>Site is down</td>
</tr>
</tbody>
</table>

<!-- auto generated rejected sources list -->
</detail>

## Get help

Questions and tips: [GitHub Discussions](https://github.com/lncrawl/lightnovel-crawler/discussions).
