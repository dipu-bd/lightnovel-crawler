# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build & Development Commands

The [Makefile](Makefile) wraps [uv](https://docs.astral.sh/uv/); `make install` / `make sync` use `uv sync --all-extras --all-groups`. Python `>=3.9`.

```bash
# Setup and install
make setup            # Ensure uv is installed
make install          # setup + uv sync (default target: `make` or `make all`)
make sync             # uv sync only
make upgrade          # setup + uv sync --upgrade

# Development servers and tooling
make start            # Run backend server (python -m lncrawl -ll server)
make watch            # Run server with auto-reload (--watch)
make lint             # ruff check + ruff format --check
make lint-fix         # ruff check --fix + ruff format
make add-source       # Guided CLI to scaffold a new source crawler
make index-gen        # Regenerate source search index (scripts/index_gen.py)
make check-sources    # Validate source crawlers (scripts/check_sources.py)

# Version (writes lncrawl/VERSION via scripts/bump.py)
make patch | minor | major

# Build
make build            # version + install + wheel + exe + installer (Windows)
make build-wheel      # python -m build -w
make build-exe        # PyInstaller (setup_pyi.py) — onedir on Windows, onefile on Mac/Linux
make build-installer  # Inno Setup → dist/lncrawl.exe installer (Windows only, no-op elsewhere)

# Dependencies (PKG is the second word; uses uv add/remove)
make add-dep <pkg>    # main dep
make add-dev <pkg>    # add to optional extra `dev`
make rm-dep <pkg>
make rm-dev <pkg>

# Docker (uses compose.yml in repo root)
make docker-base      # Calibre + system deps base image (Dockerfile.base)
make docker-build     # docker-base then app image
make docker-up | docker-down | docker-logs

# Misc
make version          # Print lncrawl/VERSION
make clean            # Remove .venv, logs, build, dist, *.egg-info, __pycache__
```

Run from source without make: `uv run python -m lncrawl [args]`.

There is **no automated test suite** — `test.py` is a developer scratchpad. Validate changes by lint, source download (`uv run python -m lncrawl -s "URL" --first 3 -f`), and running the server.

## High-Level Architecture

This project is two things in one package:

1. A **CLI/library** that scrapes individual novel sites and produces e-books.
2. A **FastAPI server + web UI** that turns the same engine into a multi-user job/library service.

Both share a single in-process `AppContext` (`ctx`) singleton; nothing is meant to span processes — concurrency is threads + asyncio inside one Python process.

### Entry points

- [lncrawl/__main__.py](lncrawl/__main__.py) → [lncrawl/app.py](lncrawl/app.py): Typer CLI. Subcommands `version`, `config`, `sources`, `crawl`, `search`, `server`, `app`, plus hidden `dev`. `app` subcommand launches the desktop webview (`lncrawl/server/webview.py`). When running as a **frozen executable** (PyInstaller), `__main__.py` calls `webview.start()` directly, bypassing the CLI.
- [lncrawl/server/webview.py](lncrawl/server/webview.py): Desktop launcher. Opens the app in Chrome/Edge app-mode; falls back to system browser + a small tkinter status window (shows URL, Copy URL, Stop Server) when no app-mode browser is found.
- [lncrawl/server/app.py](lncrawl/server/app.py): FastAPI app. `lifespan` calls `ctx.setup()` then `ctx.scheduler.start()`. API mounted at `/api`, web SPA served from `/`. OpenAPI at `/docs`, `/redoc`, `/openapi.json`.

### AppContext singleton

[lncrawl/context.py](lncrawl/context.py) defines `__AppContext__` and exports `ctx`. Every service is a `@cached_property`, so imports are deferred and a service is only constructed on first access. `ctx.setup()` boots the logger, config, DB (with Alembic migrations), creates the admin user, and loads sources. `ctx.destroy()` is registered with Typer's `call_on_close`. **Always reach shared state via `ctx.<service>`** — do not instantiate service classes directly.

Important services (from `ctx`): `config`, `logger`, `db`, `mail`, `http`, `files`, `sources`, `users`, `novels`, `tags`, `secrets`, `volumes`, `chapters`, `images`, `artifacts`, `jobs`, `history`, `libraries`, `feedback`, `announcements`, `translator`, `crawler`, `binder`, `lsp`, `scheduler`, `admin`, `github`.

### Source crawlers (the scraping layer)

- **Where**: [sources/](sources/) is grouped by language (`en/<letter>/`, `zh/`, `ja/`, `multi/`, …). User-added crawlers also load from `ctx.config.crawler.user_sources`.
- **Base classes**: [lncrawl/core/crawler.py](lncrawl/core/crawler.py) (`Crawler`, abstract — `read_novel_info` + `download_chapter_body`) and [lncrawl/core/scraper.py](lncrawl/core/scraper.py) (`Scraper`, HTTP/BS4/Cloudflare). Concurrency primitive: [lncrawl/core/taskman.py](lncrawl/core/taskman.py) (`TaskManager`, ThreadPoolExecutor wrapper).
- **Templates** ([lncrawl/templates/](lncrawl/templates/)): preferred starting point for new crawlers. `soup.general.GeneralSoupTemplate` is the recommended base — implement `parse_title`, `parse_cover`, `parse_chapter_list` (yield `Chapter`/`Volume`), `select_chapter_body`. Engine-specific templates (`madara`, `novelfull`, `novelpub`, `wordpress`, `mangastream`, `freewebnovel`, `novelmtl`) cover sites built on common platforms.
- **Discovery & registry**: [lncrawl/services/sources/service.py](lncrawl/services/sources/service.py) imports every `*.py` under the source dirs at startup, builds a `Crawler` subclass map keyed by host/URL, and maintains a full-text search index (`FTSStore`) for source lookup. A remote source index can also be pulled if `sync_remote=True`.
- **Examples & guide**: [sources/_examples/](sources/_examples/) (numbered templates `_00_basic.py` … `_17_…`); full creation guide is [.github/docs/CREATING_CRAWLERS.md](.github/docs/CREATING_CRAWLERS.md).

### Persistence layer

- ORM: SQLModel/SQLAlchemy. Models in [lncrawl/dao/](lncrawl/dao/): `User`, `UserToken`, `Novel`, `NovelTranslation`, `Volume`, `VolumeTranslation`, `Chapter`, `ChapterTranslation`, `ChapterImage`, `Library`, `LibraryNovel`, `Artifact`, `Job`, `ReadHistory`, `Tag`, `Feedback`, `Announcement`, `Secret`. Enums live in [lncrawl/enums.py](lncrawl/enums.py) and are re-exported via `dao/__init__.py`.
- DB engine: [lncrawl/services/db.py](lncrawl/services/db.py). URL comes from `ctx.config.db.url`; defaults to local SQLite, supports PostgreSQL via `DATABASE_URL`.
- Migrations: [lncrawl/migrations/](lncrawl/migrations/) (Alembic). `ctx.db.bootstrap()` runs migrations on startup.

### Background work: jobs + scheduler

- [lncrawl/services/jobs/](lncrawl/services/jobs/) — `JobService` is the persistence/query API for `Job` rows.
- [lncrawl/services/scheduler/](lncrawl/services/scheduler/) — `JobScheduler` (started in FastAPI `lifespan`) spawns worker threads: `JobRunner` runs novel-fetching/downloading jobs, `Scrubber` performs cleanup. Concurrency comes from `ctx.config.crawler.runner_concurrency`.
- Job status is polled via the REST API; there is no dedicated job WebSocket. The only WebSocket endpoint (`/api/lsp`) is the Language Server Protocol proxy (`ctx.lsp`) — it spawns a per-session `pylsp` subprocess and relays JSON-RPC over TCP.

### Output / binding

[lncrawl/services/binder/](lncrawl/services/binder/) generates artifacts. EPUB is the native format (`epub.py`); other formats (MOBI, PDF, AZW3, DOCX, FB2, …) are produced by shelling out to Calibre's `ebook-convert` (`calibre.py`); `json.py` and `text.py` are dependency-free outputs.

[lncrawl/services/translators/](lncrawl/services/translators/) (`ctx.translator`) machine-translates novel content (chapters, volumes, titles) into a target language. Wraps multiple backends — Bing, Google (three variants), Lingva, Baidu — with automatic failover when a backend fails. Translation results are stored as `*Translation` DAO rows alongside the originals.

[lncrawl/services/github.py](lncrawl/services/github.py) (`ctx.github`) fetches and caches the remote source index from GitHub (throttled to one fetch per 60 s) and supports downloading individual source files into `user_sources` or submitting new crawlers as GitHub PRs.

### Server API

Routers live in [lncrawl/server/api/](lncrawl/server/api/) and are aggregated in [lncrawl/server/api/__init__.py](lncrawl/server/api/__init__.py). Auth is enforced per-router via `Security(ensure_user)` / `Security(ensure_admin)` / `Security(ensure_local)` from [lncrawl/server/security.py](lncrawl/server/security.py). `ensure_admin` requires `UserRole.ADMIN`; `ensure_local` requires the `LOCAL` scope token but still checks `role == ADMIN` at runtime (it is scoped for local-process callers that skip normal auth). The `lsp` WebSocket router handles its own auth (token query param) and is mounted **before** the HTTP routers so it doesn't inherit HTTP security deps. The `/settings` router carries per-user notification preferences. Tier/quota logic in [lncrawl/server/tier.py](lncrawl/server/tier.py).

Pydantic request/response models live in [lncrawl/server/models/](lncrawl/server/models/), distinct from the SQLModel persistence models in `dao/`.

### Configuration

[lncrawl/config.py](lncrawl/config.py): typed config with cached properties. Data dir resolves from env `LNCRAWL_DATA_PATH` first, otherwise `typer.get_app_dir("LNCrawl", force_posix=True, roaming=True)` — on Windows this is `%APPDATA%\LNCrawl`. Config file defaults to `<data>/config.json`. Properties annotated with `Sensitive` are flagged in the admin API.

## Windows Packaging

`setup_pyi.py` drives PyInstaller. Platform behaviour differs deliberately:

| Platform | Mode | Output |
|----------|------|--------|
| Windows | `--onedir` | `dist/lncrawl/` directory (fast startup — no extraction step) |
| Mac / Linux | `--onefile` | `dist/lncrawl` single binary |

After `build-exe` on Windows, `make build-installer` (or the CI step) compiles [installer/installer.iss](installer/installer.iss) with Inno Setup 6 into `dist/lncrawl.exe` — a self-contained installer that handles install, upgrade, uninstall, optional desktop shortcut, and optional PATH entry. Inno Setup 6 is pre-installed on GitHub Actions `windows-latest` runners.

Key installer design decisions:
- **Per-user install by default** (`PrivilegesRequired=lowest`) — no UAC prompt. Users can opt into a machine-wide install via the dialog.
- **Stable `AppId` GUID** in `installer.iss` — never change it; Inno Setup uses it to identify upgrades and the uninstaller entry.
- The installed `lncrawl.exe` inside Program Files won't carry the "downloaded from internet" zone marker, so Windows won't flag it as dangerous at launch. The installer itself requires a code-signing certificate to suppress SmartScreen (see comment at the top of `installer.iss`).

## Adding a New Source Crawler

Full guide: [.github/docs/CREATING_CRAWLERS.md](.github/docs/CREATING_CRAWLERS.md).

Recommended path: copy [sources/_examples/_01_general_soup.py](sources/_examples/_01_general_soup.py) into the right folder (`sources/en/<letter>/`, `sources/zh/`, etc.), rename the class, set `base_url`, and implement the four required methods. For search use `_02_searchable_soup.py`; for explicit volumes use `_05_with_volume_soup.py` / `_07_optional_volume_soup.py`; for JS-rendered sites use the browser examples (`_09`–`_17`).

Test a crawler end-to-end:

```bash
uv run python -m lncrawl crawl "https://site.com/novel/example" --first 3 -f epub
uv run python -m lncrawl sources list   # confirm registration
```

## Conventions worth knowing

- **Lazy imports inside `ctx` properties** are intentional — keeps CLI startup fast and avoids importing the FastAPI/DB stack for `lncrawl crawl`. Don't move imports to module top in `context.py`.
- **`ruff` config** ([pyproject.toml](pyproject.toml)): line-length 100, double quotes, target py39. Excludes `lncrawl/cloudscraper` (vendored), `lncrawl-web`, `res`, `logs`, `Lightnovels`, `.github`.
- README.md is **partially auto-generated** (the source list and CLI help blocks). Don't hand-edit those regions; regenerate via the appropriate script.
- The vendored [lncrawl/cloudscraper/](lncrawl/cloudscraper/) is a fork — apply upstream-style patches there rather than refactoring.
