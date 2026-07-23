---
name: add-source
description: Create or fix a source crawler — base-class choice (SoupTemplate/LegacyCrawler/shared templates), selectors, cleaner tuning, testing via CLI, index-gen. Use when adding a new source site, fixing a broken crawler, or working in sources/ or lncrawl/templates/.
---

# Source crawlers

Sources live in `sources/` grouped by language dir (`en/` is sub-bucketed by first letter:
`sources/en/<letter>/<file>.py`; other languages are flat). There is **no scaffold command** —
copy a similar existing source. The loader (`services/sources/helper.py`) skips files starting
with `_`, abstract classes, classes with `is_template = True`, and classes without a valid
`base_url` — a "missing" crawler is usually one of these. User-provided sources are discovered
the same way from `ctx.config.crawler.user_sources` (a dir under the app data dir).

## Class hierarchy — pick your base

- **`SoupTemplate`** (`lncrawl/core/template.py`) — the default for new sources. Declarative
  CSS selectors; extends `BrowserTemplate`, so failed fetches transparently retry through a
  real browser (`nodriver`), which covers most JS/Cloudflare sites for free.
- **A shared template in `lncrawl/templates/`** — if the site runs a known engine
  (WordPress/Madara, NovelFull, NovelMTL, MangaStream, FreeWebNovel, NovelPub, …), subclass
  the matching template and override only what differs. This is the most common shape for new
  sources and usually ~10 lines.
- **`LegacyCrawler`** (`lncrawl/core/legacy.py`) — the classic imperative API
  (`read_novel_info`, `download_chapter_body`, optional `search_novel`, instance attrs
  `novel_title`/`chapters`/`volumes`, helper `self.get_soup`). Most existing sources use it;
  fine to match when fixing one, but prefer `SoupTemplate` for new work.
- **`Crawler`** (`lncrawl/core/crawler.py`) — the raw abstract base. Its modern abstract
  methods are `read_novel(novel)` / `download_chapter(chapter)` — **not** the legacy names;
  the two APIs must not be mixed in one class.

The `Scraper` (HTTP/BS4/Cloudflare) comes from the external **`lncrawl-scraper`** package
(`from scraper import Scraper`) — there is no scraper module inside this repo. `PageSoup`
selectors are null-safe: `select_one()` always returns a (possibly falsy) `PageSoup`, never
`None`.

## SoupTemplate essentials

Class attributes: `base_url` (str or list — always required), `language`, and flags
`can_search`, `can_login`, `has_manga`, `has_mtl`. Selector groups:

- Novel: `novel_title_selector`, `novel_cover_selector`, `novel_author_selector`,
  `novel_tags_selector`, `novel_synopsis_selector` (defaults fall back to OpenGraph/meta).
- Chapters: `chapter_list_selector`, `chapter_title_selector`, `chapter_url_selector`,
  `chapter_body_selector`, `chapter_list_reverse`.
- Volumes: `volume_list_selector`, `volume_title_selector` — leave empty and `format_novel`
  auto-buckets chapters into volumes of `chapters_per_volume`.
- Search: `search_item_*` selectors + `build_search_url(query)` (must override when
  `can_search`).

When selectors can't express it, override the hooks: `parse_title/cover/authors/tags/summary`,
`select_volume_tags`, `select_chapter_tags`, `parse_chapter_title/url`, `build_chapter_url`,
`parse_chapter_body`, `get_novel_soup`. Chapter-list pagination has no framework helper —
loop pages inside `select_chapter_tags` (see existing sources that do this).

## Idioms that matter

- **URLs**: route every href/src through `self.absolute_url(x)`. It resolves against
  `scraper.last_soup_url`, which only `get_soup`/`post_soup` set — after raw `get()`/
  `get_json()`, pass `page_url=` explicitly.
- **Cleaner**: chapter HTML goes through `self.cleaner` (`TextCleaner`,
  `lncrawl/core/cleaner.py`). Tune it in `initialize()`: `self.cleaner.bad_css.update({...})`
  for ad/nav selectors, `bad_tag_text_pairs` to drop tags whose text matches a pattern,
  `whitelist_attributes`/`whitelist_css_property` to keep extras.
- **Concurrency/rate limits**: declare static class fields — `request_concurrency = N`
  (max requests in flight to this source; default 1) and/or `request_rate_limit = R` (max
  requests/sec; implies serial requests). These are enforced **globally per source domain**
  across all concurrent server jobs via a shared limiter (`init_crawler` in
  `services/sources/service.py`), and drive the CLI's worker pool. Do **not** call
  `init_executor` in `initialize()` — that's the legacy pattern and is dead in server mode.
  Many sites ban parallel scrapers — when in doubt, keep the default.
- **Headers/cookies/login**: `self.scraper.set_header/set_cookie`; implement `login()` and set
  `can_login = True`. `Origin`/`Referer` are auto-injected — leave them unless the site
  objects.
- **`format_novel` renumbers everything** (sorts, re-ids, buckets orphan chapters) — don't
  rely on your assigned ids; set correct `chapter.volume` grouping instead.
- Data models (`lncrawl/core/models.py`): `Novel`/`Volume`/`Chapter`/`SearchResult` are
  Box-based (attribute access, extra kwargs preserved); use `novel.add_volume(...)` /
  `novel.add_chapter(...)` which auto-assign ids.

## Workflow

1. Create `sources/<lang>/[<letter>/]<site>.py` by copying the closest existing source or
   template subclass.
2. Implement (see above). Type-annotate signatures; f-strings only.
3. Test against a real novel:
   ```bash
   uv run python -m lncrawl crawl "https://site/novel/x" --first 3 -f epub --noin
   ```
   Verify title, cover, TOC count, and readable chapter bodies. The web Source Editor's
   streaming tester (`services/sources/tester.py`) is the reference for what "passing" means —
   it reads the novel then downloads the first and last chapters.
4. `make lint`.
5. `make index-gen` — regenerates `sources/_index.json`/`.zip` **and the auto-generated
   README source tables**. Required whenever a source is added/renamed or its
   `base_url`/flags change, before the change is complete. (`make check-sources` is only an
   HTTP reachability probe of base URLs that feeds `sources/_rejected.json` — it does not
   validate crawler code.)

## Browser fallback

`BrowserTemplate` retries failed `get_soup`/`get_image`/`get_json` through a real Chrome via
`nodriver`; direct `Browser` usage (`lncrawl/core/browser.py`: `visit`, `soup`, `find`,
`execute_js`, `wait`) is rarely needed. Gated by `ctx.config.crawler.can_use_browser`;
headless mode is off by default because a visible window evades bot detection.
