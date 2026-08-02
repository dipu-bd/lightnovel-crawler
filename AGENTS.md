# AGENTS.md

Guidance for Claude Code working in this repo —
[Lightnovel Crawler](https://github.com/lncrawl/lightnovel-crawler): a **CLI scraper** that
produces e-books and a **FastAPI server + web UI** that turns the same engine into a
multi-user job/library service, in one package. Both share a single in-process `AppContext`
(`ctx`) singleton — concurrency is threads + asyncio inside one Python process. The web UI
source lives in the sibling `lncrawl-web` repo; the HTTP `Scraper` lives in the external
`lncrawl-scraper` package (imported as `scraper`) — **1.0+**, which is organised around a
model of bot detection rather than a request pipeline. Two consequences show up here:
the profile owns the header set and the User-Agent (never set one), and per-origin state
is shared via one process-wide `SharedState` owned by `ctx.scraper`
([services/scraper.py](lncrawl/services/scraper.py)) — the only place a `Scraper` is
constructed.

## Skills

Deep, task-scoped knowledge lives in `.claude/skills/`. **Read the matching skill before
starting work in its area** — they hold the recipes and invariants this file only points to:

| Skill                    | Use when                                                                          |
| ------------------------ | --------------------------------------------------------------------------------- |
| `add-source`             | Creating/fixing a source crawler; anything in `sources/` or `lncrawl/templates/`  |
| `add-api-endpoint`       | Server routes, security, DTOs, pagination, errors (`server/`)                     |
| `add-job-type`           | Job kinds, handlers, scheduler behavior (`services/scheduler/`, `services/jobs/`) |
| `db-migration`           | DAO model changes and Alembic migrations (`dao/`, `migrations/`)                  |
| `output-and-translation` | Output formats (binder) and the translation service                               |
| `releasing`              | Version bumps, the tag-triggered release pipeline, CI workflows                   |

## Build & development commands

Toolchain: [uv](https://docs.astral.sh/uv/), Python per `pyproject.toml`. The
[Makefile](Makefile) wraps all common tasks — read it for the full target list.

```bash
make install       # setup + uv sync --all-extras --all-groups
make start         # run the server (make dev = with auto-reload)
make lint          # pyright lncrawl + ruff format --check + ruff check — run before finishing
make lint-fix      # ruff check --fix + ruff format
make index-gen     # regenerate source index + SOURCES.md tables
make check-sources # HTTP reachability probe of source base URLs (NOT a code validator)
```

Run without make: `uv run python -m lncrawl [args]`.

`uv run python -m lncrawl dev check-sources` is the code validator: it imports and instantiates
every crawler offline, asserts the delegation surface each base class promises, and fails if a
crawler in `sources/_index.json` no longer loads. Run it after anything that touches `core/`,
`lncrawl/templates/` or a batch of sources.

**No automated test suite** — `test.py` is a scratchpad. Validate with lint, then exercise the
real thing, e.g.:

```bash
uv run python -m lncrawl crawl "https://site.com/novel/url" --first 3 -f epub
```

## Architecture

### AppContext (`ctx`)

[lncrawl/context.py](lncrawl/context.py) exports `ctx`, the service registry — read it for
the current service list. Every service is a `@cached_property` with a **function-local lazy
import** returning a no-arg constructor: constructed on first access, never before. The lazy
import is load-bearing — it keeps `lncrawl crawl` from importing the FastAPI/DB stack.
**Always use `ctx.<service>`; never instantiate service classes directly** (services reach
each other the same way).

- `ctx.setup()` boots logger → config → DB (Alembic migrations) → seed data (admin user,
  secrets) → sources. `ctx.destroy()` closes resource-holding services, guarded by
  `if "<name>" in self.__dict__` so never-touched services aren't constructed at shutdown —
  the guard string must match the property name exactly.
- **Adding a service**: new `@cached_property` with lazy import; no constructor args; add a
  `destroy()` guard if it holds threads/connections/files; add a `setup()` call only for
  boot-time initialization; server-start background work goes in the FastAPI lifespan
  instead.
- Notable services: **`ctx.tier`** (`AccessManager`, [services/access.py](lncrawl/services/access.py))
  — every quota/permission check goes through `ctx.tier.<check>(user)`; limits are per-tier
  class dicts where `None` means unlimited. **`ctx.scraper`** (`ScraperService`,
  [services/scraper.py](lncrawl/services/scraper.py)) — the only place a `Scraper` is built;
  `open()` for crawl traffic (paced, remembered, routed through the configured exits) and
  `plain()` for everything else. **`ctx.http`** ([services/fetch.py](lncrawl/services/fetch.py))
  wraps `plain()` for non-crawl HTTP (translators, Calibre API, favicons); pass `signal=`
  per request rather than assigning it to the session. **`ctx.job_notifier`** — job-state
  emails, triggered automatically by handler helpers.

### Entry points

- [lncrawl/\_\_main\_\_.py](lncrawl/__main__.py) → `main()` in `lncrawl/__init__.py`: frozen
  (PyInstaller) double-click launches the desktop webview; an env flag re-execs the exe as
  the Python LSP server; otherwise the Typer CLI in [lncrawl/app.py](lncrawl/app.py)
  (`version`, `config`, `sources`, `crawl`, `search`, `server`, `app`, plus a hidden `dev`
  group with the migration commands).
- [lncrawl/server/app.py](lncrawl/server/app.py): FastAPI app. `lifespan` runs `ctx.setup()`
  then starts the background services (mail, scheduler, recommendation warmup) and
  `ctx.destroy()`s on exit. API at `/api`, SPA at `/`, Swagger at `/docs`, `/health` for
  liveness.
- [lncrawl/server/webview.py](lncrawl/server/webview.py): desktop launcher — Chrome/Edge
  app-mode, fallback to system browser; logs in via a LOCAL-scope `?authToken=`.

### Job scheduler

[lncrawl/services/scheduler/](lncrawl/services/scheduler/) — `JobScheduler` spawns daemon
worker threads: general job runners, a dedicated artifact-only worker, a `Scrubber` cleanup
loop, and a stale-job reset loop. `JobRunner._claim_next()` does find-and-claim under a
module-level `EventLock` (fairness: one running job per user and per source domain);
`run_job()` executes outside the lock, dispatching to the first matching handler in
`_HANDLER_REGISTRY`. Cancellation is **cooperative** — a per-claim `Event` that handlers
poll; nothing kills threads. Job status is polled via REST; the only WebSocket is `/api/lsp`.
Full contracts and the add-a-job-type recipe: **`add-job-type` skill**.

### Source crawlers

Sources live in [sources/](sources/) grouped by language; user sources load from
`ctx.config.crawler.user_sources`. Base classes in [lncrawl/core/](lncrawl/core/):
`Crawler` (abstract) → `CrawlerTemplate` → `SoupTemplate` (declarative selectors — preferred
for new sources) and `LegacyCrawler` (the classic `read_novel_info`/`download_chapter_body`
API most existing sources use). **A source never drives a browser**: the scraper escalates
to one on its own evidence, and a page whose HTML is not its content is fetched with
`self.scraper.render_soup(url, wait_for=…)`. Shared site-engine templates (WordPress/Madara,
NovelFull, …) live in [lncrawl/templates/](lncrawl/templates/) — subclassing one is usually a
~10-line source. There is no scaffold command; copy a similar source. After adding/renaming a
source: `make index-gen`. Everything else: **`add-source` skill**.

### Persistence

SQLModel/SQLAlchemy; models in [lncrawl/dao/](lncrawl/dao/) (all extend `BaseTable`: UUID id,
UNIX-ms timestamps, JSON `extra`). Enums in [lncrawl/enums.py](lncrawl/enums.py),
re-exported from `dao/__init__.py`, stored **by name** (native ENUM on Postgres → enum
changes need a sync migration). SQLite by default, Postgres/MySQL via `DATABASE_URL`;
Alembic migrations run automatically on startup via the `dev migrate` CLI machinery.
Recipe: **`db-migration` skill**.

### Server API

Routers in [lncrawl/server/api/](lncrawl/server/api/), aggregated with router-level
`Security(ensure_user)`/`ensure_admin` dependencies in its `__init__.py`. Pydantic DTOs in
[server/models/](lncrawl/server/models/) are distinct from the DAO models. Errors are
pre-instantiated `ServerErrors` singletons ([lncrawl/exceptions.py](lncrawl/exceptions.py)) —
never hand-roll `HTTPException`. [server/web/](lncrawl/server/web/) is committed build
output synced from lncrawl-web — never hand-edit. Recipes: **`add-api-endpoint` skill**.

### Output & translation

**Binder** ([services/binder/](lncrawl/services/binder/)): EPUB/JSON/text native; every other
format converts from EPUB via Calibre (local exe or remote API). **Translation**
([services/translators.py](lncrawl/services/translators.py)): in-process via the external
`lncrawl-translator` package — lncrawl owns the glossary loop and persistence, the package
owns engines/routing/failover; its dashboard is mounted admin-gated at `/api/translator`.
Recipes: **`output-and-translation` skill**.

### Configuration

[lncrawl/config.py](lncrawl/config.py): typed config — `_Section` subclasses exposing
`@property` getter/setter pairs over a JSON-persisted store; property docstrings surface in
the admin settings UI. Secrets are marked `Annotated[..., Sensitive]` and redacted in the
admin API. Data dir: `LNCRAWL_DATA_PATH` env var, else the platform app dir; `DATABASE_URL`
and `LNCRAWL_CONFIG` override DB and config file; `.env` is auto-loaded.

## Conventions

- **ruff** ([pyproject.toml](pyproject.toml)) + **pyright** — the pyproject is the source of
  truth for line length, quote style, target version, and excluded dirs.
- **f-strings** for all string interpolation and **type annotations** on function signatures
  and variable declarations — house conventions (not machine-enforced; follow them anyway).
- **SOURCES.md** source tables and the **README.md** CLI help and source-count blocks between
  `<!-- auto generated -->` markers are rewritten by `make index-gen` — don't hand-edit those
  regions, and keep each marker paired. `README.md` is also the PyPI long description, so
  every link and image in it must be an absolute URL. `CHANGELOG.md` sections
  are curated by hand and become release notes.
- **`CHANGELOG.md`: one line per paragraph, and keep entries short.** The release workflow
  lifts a version's section out verbatim, and the renderer on the other side turns a single
  newline into a line break — so never hard-wrap, or the paragraph arrives as a ragged
  column with its indentation showing. (Blank lines still separate paragraphs, and a
  continuation paragraph inside a bullet still needs its indent.) An entry is a bold lead
  sentence plus the shortest _why_ that would stop someone undoing it — not the
  investigation that produced it. Reasoning at length belongs in the code comment or the
  docstring, where the reader is already looking at the thing it explains.
- Prefer patching over refactoring in vendored/generated areas; `lncrawl/server/web/` and
  `sources/_index.*` are generated.

## Commits

- **Never commit or push automatically.** When work is done, pause and ask; at most draft a
  commit message for the user to commit themselves. Only run `git commit` when the user
  explicitly requests it in that moment — prior approval does not carry over.
- **No AI attribution trailers** — never append `Co-Authored-By: Claude` (or similar).
- Message style: imperative subject, no type prefix; body bullets for non-trivial changes.
