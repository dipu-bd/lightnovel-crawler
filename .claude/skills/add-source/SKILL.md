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
  CSS selectors over `self.scraper.get_soup`. Challenges are the scraper's problem, not the
  source's: it escalates to a browser on its own evidence.
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
  `scraper.last_url`, which only `get_soup`/`post_soup` set — after raw `get()`/
  `get_json()`, pass `page_url=` explicitly.
- **Cleaner**: chapter HTML goes through `self.cleaner` (`TextCleaner`,
  `lncrawl/core/cleaner.py`). Tune it in `initialize()`: `self.cleaner.bad_css.update({...})`
  for ad/nav selectors, `bad_tag_text_pairs` to drop tags whose text matches a pattern,
  `whitelist_attributes`/`whitelist_css_property` to keep extras.
- **Rate limit**: declare the static class field `request_rate_limit = R` (max requests/sec
  to this source; default 3). It is enforced **globally per source domain** across all
  concurrent server jobs: `init_crawler` (`services/sources/service.py`) builds one
  `scraper.SharedState` per domain and hands it to every crawler for that domain, so the
  pacing clock, the held exit address and the identity are one visitor rather than
  several contradicting each other. The rate is a *mean* — each gap is drawn from a
  distribution around it, because a constant interval is itself a signal. The
  parallel-request cap and CLI worker pool derive from it (`Crawler.max_concurrency()`).
  Do **not** call `init_executor` in `initialize()` — that's the legacy pattern and is dead in
  server mode. Many sites ban parallel scrapers — when in doubt, keep the default.
- **Headers/cookies/login**: `self.scraper.headers` is a plain dict you can write to, and
  `self.scraper.set_cookie(name, value)` sets a cookie; implement `login()` and set
  `can_login = True`. Do **not** try to set a `User-Agent` or reorder headers — the
  impersonation profile owns the header set, and header *order* is read as a
  fingerprint. `Referer` and the `Sec-Fetch-*` set are supplied per request by the
  scraper's navigation chain; leave them alone.
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

## When plain HTTP is not enough

**A source never drives a browser.** A challenge is a detection layer, and the scraper
escalates to its own solver when its diagnosis says one is binding — reusing the clearance
for the requests that follow, which a browser a source opened itself cannot do.

The one case a source decides is different: a page that answers `200` with a shell that
JavaScript fills in. Nothing is blocking, so no diagnosis leads there and the scraper cannot
infer it — the source must say so with `self.scraper.render_soup(url, wait_for="…")`. Give it
a `wait_for` that **cannot exist before the data does**; a selector matching an empty
skeleton returns a page that parses to nothing. Prefer an API the site's own front-end calls
over rendering when one exists: it is faster, and it does not depend on a selector.
