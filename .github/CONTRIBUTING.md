# Contributing

Thanks for contributing! The most common contributions are:

- **Source crawlers** — adding or fixing support for a novel site
- **Bug fixes** — fixing crashes, wrong output, or server issues
- **Features** — new capabilities in the CLI or web server

---

## Dev setup

Requires [uv](https://docs.astral.sh/uv/) and Python 3.9+.

```bash
git clone https://github.com/lncrawl/lightnovel-crawler.git
cd lightnovel-crawler
make install   # sets up venv and installs all dependencies
```

Start the server with auto-reload while you work:

```bash
make dev
```

Or run the CLI directly:

```bash
uv run python -m lncrawl crawl "https://example.com/novel/url" --first 3 -f epub
```

---

## Code style

The project uses **ruff** (formatting + linting) and **pyright** (type checking).

```bash
make lint       # check — runs pyright, ruff format --check, ruff check
make lint-fix   # auto-fix ruff issues and reformat
```

Rules to keep in mind:

- Line length: 100, double quotes, target Python 3.9 — `pyproject.toml` is the source of truth
- HTTP goes through the external [`lncrawl-scraper`](https://github.com/lncrawl/scraper) package. It owns the headers and the User-Agent, and it decides on its own evidence when a page needs a browser — never set those from a source or drive a browser yourself

Run `make lint` before opening a PR and fix any errors it reports.

---

## Adding a source crawler

This is the most common contribution. Each source is a single Python file.

### 1. Find the right directory

Sources are organized by language; English is further bucketed by the first letter of the file name:

```text
sources/
  en/a/   ← English sites starting with "a"
  zh/     ← Chinese
  multi/  ← multilingual
  ...
```

Create your file at `sources/en/<letter>/sitename.py`, or `sources/<lang>/sitename.py` for every other language. There is no scaffold command — copy a similar existing source. A file whose name starts with `_` is skipped by the loader.

### 2. Pick a base class

Check `lncrawl/templates/` first — if the site runs a known engine (WordPress/Madara, NovelFull, NovelMTL, MangaStream, FreeWebNovel, NovelPub, Blogger) the matching template already knows how to crawl it, and your source is about ten lines:

```python
from lncrawl.templates.madara import MadaraTemplate

class MySiteCrawler(MadaraTemplate):
    base_url = ["https://mysite.com/"]
```

Otherwise subclass **`SoupTemplate`** and declare selectors. This is the base class for all new sources:

```python
from lncrawl.core import SoupTemplate

class MySiteCrawler(SoupTemplate):
    base_url = ["https://mysite.com/"]
    language = "en"
    has_mtl = False
    has_manga = False
    can_search = False

    novel_title_selector = "h1.entry-title"
    chapter_list_selector = ".chapter-list a"
    chapter_body_selector = ".chapter-content"
```

The title, cover, author, tags and synopsis fall back to OpenGraph and meta tags, so a site that publishes those needs only the chapter selectors. When a selector cannot express something, override the hook for it (`select_chapter_tags`, `parse_chapter_body`, `build_search_url`, …) rather than reaching for a different base class.

`LegacyCrawler` (`read_novel_info` / `download_chapter_body`) is what most existing sources still use. Match it when you are fixing one of those; do not start a new source with it.

### 3. Validate

```bash
uv run python -m lncrawl dev check-sources
```

That imports and instantiates every crawler offline and fails on anything that no longer loads. (`make check-sources` is a different thing — an HTTP probe of source base URLs, not a code check.)

Then do a real crawl:

```bash
uv run python -m lncrawl crawl "https://mysite.com/some-novel" --first 3 -f epub
```

Open the EPUB and read a chapter. A crawl that "succeeds" with empty or advert-filled chapters is the usual failure — a challenge page and an ad page both answer `200`.

### 4. Open a PR

One source per PR. Include the site URL in the PR title, e.g. `Add mysite.com`.

Do not commit `sources/_index.json`, `sources/_index.zip` or `SOURCES.md` — CI regenerates all three after your PR lands.

---

## Opening a PR

- **One logical change per PR.** If you are fixing a bug and adding a source, open two PRs.
- Run `make lint` and fix all errors before pushing.
- For source PRs: include a novel URL you tested against in the PR description.
- For bug fixes: describe what was wrong and how you verified the fix.

### CI on forks

Lint and build workflows run on forks automatically. See [FORKING.md](FORKING.md) for details on how CI works and how to download build artifacts from your fork.

---

## Questions?

Open a [Discussion](https://github.com/lncrawl/lightnovel-crawler/discussions) rather than an issue if you are unsure about something or want feedback before starting.
