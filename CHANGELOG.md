# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Upgraded to `lncrawl-scraper` 1.0**, a rewrite of the HTTP layer around a model of
  bot detection. Measured on 150 real source hosts it retrieves more of them than the
  version it replaces, with no fallback to a cached copy. What changed here:

  - Proxy configuration keeps the same `crawler.proxy_urls` format, but each entry now
    becomes a typed *exit*: the new scraper describes an address by kind, because what a
    detector reads is the reputation of the range it belongs to. Plain URLs are treated
    as datacenter addresses, which is the conservative reading — it never claims reach
    the address does not have.
  - A new `torpool;<api_url>;<socks_url>;<token>` entry form for
    [tor-pool](https://github.com/lncrawl/tor-pool), which fronts many Tor instances
    behind one sticky SOCKS port and reassigns on demand.
  - The legacy `tor;<host>;<port>;<control_port>;<password>` form still works, and the
    control port is now accepted and ignored. Rotation by `NEWNYM` is gone: it has a
    ~10s cooldown and no say in which exit comes next, so a rotation could land on the
    same relay. Use `torpool;` for real rotation.
  - `allow_fallback_on_proxy_miss` still does what it says, by adding a direct entry to
    the exit list. The scraper dropped its own fallback-to-direct switch, because
    silently leaving the proxy mid-session is how a scrape leaks the host's real
    address — but naming direct as *one of* the available exits is a different thing,
    and that is now how it is expressed.
  - `request_rate_limit` is a **mean** rather than a floor. Each gap is drawn from a
    distribution around it, because a constant interval is itself something a
    behavioural model reads. It is still enforced per source domain across concurrent
    jobs, now through shared per-origin state rather than a limiter object — which also
    shares the held address, the identity and the referrer chain, so two jobs on one
    source look like one visitor instead of two contradicting each other.
  - A source must not set a `User-Agent` or reorder headers. The impersonation profile
    owns the header set and its order is read as a fingerprint.

- **lncrawl no longer drives a browser.** The webdriver stack it used to open Chrome with is
  gone, along with the fallback that re-fetched any failed page through it. That fallback
  fired on anything the transport raised — including a plain `404`, which cost a browser
  launch and returned a rendered error page instead of an error. Deciding when a real browser
  is needed now belongs to the scraper, which does it from its own diagnosis and reuses the
  clearance for the requests that follow. A source that needs a rendered page asks for one
  explicitly. `BrowserTemplate` and `Browser` are removed; importing either names the
  replacement instead of failing as a missing attribute, since sources are downloaded to disk
  and a user's copy may still refer to them.

- **Challenges are solved through one browser for the whole process**, and only when a
  browser is actually installed. The setting that allows browser crawling defaults to on
  while an installation need not have a browser, so it is checked as well as the setting:
  a solver that cannot launch would otherwise spend its whole timeout per site and report
  that as though the site had blocked us. A clearance earned in the browser is reused by
  the requests that follow it.

- **New `impersonate` setting.** Solving a challenge forces every request to present itself
  as Chrome, because a clearance is only valid for a client that still looks like the one
  that earned it. Set this to keep a different fingerprint instead. Removed
  `selenium_grid`, which nothing has read since browsers stopped being driven here.

- **One scraper state for the process.** What is learned about a site — the pacing
  clock, the held address, the identity, the referrer chain, the tier that worked — is
  now shared process-wide instead of per domain, so it accumulates across every job
  rather than being rebuilt and partly overwritten. Per-source rate limits and the
  per-address concurrency bound are unaffected: both are keyed per origin.

- **Non-crawl HTTP no longer pretends to be a visitor.** Requests to our own Calibre and
  translator APIs, the source index and favicons went through a crawl-shaped session,
  which meant a warm-up request to the target's homepage and a pacing wait before each
  one. They now use a session that neither waits, warms up nor remembers.

- **18 source domains are flagged as rejected**, each confirmed on a deep page rather than
  a homepage: parked domains for sale, redirects into an ad network or an affiliate link,
  one closed site, one zone whose DNS no longer resolves anywhere valid, and one whose
  domain was resold and now hosts an unrelated service. None of them reported an error — a
  page full of adverts answers `200`, so a crawl of them succeeded and produced an empty
  book.

- **`wordexcerpt` and `webnovelonline` rebuilt against the APIs their sites now use.** Both
  were rewritten as single-page apps, so the HTML their old selectors read is an empty
  shell and both had been returning nothing. Each now reads the same backend the site's
  own front-end reads, which needs no browser. `webnovelonline`'s chapter listing is
  paginated, and the whole listing is walked: the novel checked reports **1305 chapters**,
  where the page itself only ever shows the first 50.

- A scheduled *fetch latest* job asks whether the table of contents has moved before
  re-reading it, and skips the read when the site answers that it has not. Reading a
  paginated table of contents costs a request per page before a single chapter can be
  skipped. The missing-chapter pass still runs either way, so chapters absent from an
  earlier failure are still recovered.

- **A failed job says why, instead of showing a stack trace.** When a site refuses a
  request, blames a proxy, answers `404`, or serves something that is not the image it
  claimed, the job now carries the conclusion in plain words: which detection layer is
  binding, what that layer reads, and therefore whether any setting could help — a
  layer that reads a credential cannot be talked around, while one that reads an address
  is answered by configuring a proxy. The same facts are stored as separate fields, so
  none of it has to be recovered by reading the sentence.

- **A job's error is the message; the stack is kept beside it.** Every failure used to
  store its traceback and its message in one string, so each reader had to guess which
  line of it to show and all of them guessed the last one — which is why a failure email
  reported a Python exception rather than what went wrong. The message now stands alone
  and the full traceback moves to the job's `traceback` field, unchanged and untruncated.
  Nothing is discarded; the same content is simply no longer in one blob. A failure
  nothing anticipated also now says so in as many words, rather than reporting itself as
  "Failed to create requests" whatever it was doing.

- **New admin endpoint, `GET /api/source/{domain}/diagnosis`.** Answers "why is this
  source failing" for one site: what the scraper concluded about its defences, the
  pacing and success counters it learned, whether a browser clearance is held, and a
  count of what this run needed beyond a plain fetch — including chapters that came back
  empty. That last part is the distinction nothing surfaced before: a site blocking us
  and our own selectors having gone stale look identical from the outside. A rejected
  domain is explained rather than refused, which is also now true of `lncrawl dev
  explain`; a rejected domain is the one whose diagnosis is most worth reading.

- **Six crawler settings exposed**: how many requests may be in flight to one site, how
  many attempts and how many proxy addresses one page may cost, how long the browser may
  spend on one challenge, and whether pages may be read from the Web Archive along with
  how old a snapshot may be. Archive reading is what can still recover a novel from a
  site that has gone down for good, and it is off by default because with it on the first
  visit to *every* site goes to a snapshot. Each is range-checked where it is set, and a
  crawler setting now takes effect without a restart.

### Fixed

- **An empty chapter is no longer saved and marked finished.** When a site changed its
  markup the body came back empty, and nothing checked: the empty file was written, the
  chapter was marked done, and a later run skipped it because it looked complete. This is
  the most common way a source breaks and there was no signal for it anywhere. An empty
  body is now a failure — nothing is written, it is fetched again on the next pass, and
  after a few attempts it is left alone so a chapter that is genuinely empty upstream is
  not asked for forever. Each occurrence is counted against the source. A chapter that
  already had content keeps it, since an empty answer now is no reason to destroy a body
  that worked before, and image-only chapters are unaffected.

- **`lncrawl dev recover-empty-chapters`** finds chapters an earlier version stored empty
  and lets them be downloaded again. Without it the fix above changes nothing for a
  library that already has them: they are marked done, so every later run skips them. It
  reports by default and only changes anything with `--apply`.

- **What a crawl learned is no longer lost when the command exits.** State was written
  on a timer and nothing flushed it at the end, so anything learned after the first
  write — including the validators the check above depends on — was discarded.

- **A source that chooses its own HTML parser is finally obeyed.** Six sources set one
  because the default cannot handle their markup; the value was stored on the crawler
  and never reached the session that builds the soup.

- **A source's primary address no longer changes between runs.** Where a source lists
  several addresses, the one treated as its home was picked from an unordered set, so it
  varied from one run to the next for the same unchanged code — and a source listing both
  `http` and `https` for the same site could end up pinned to the plaintext one. Secure
  addresses now come first, the source's own order is kept within that, and three sources
  stop defaulting to `http`. This also makes the generated source index reproducible: it
  was rewriting a hundred lines on every build with nothing behind it.

- **`urllib3` is no longer held on the 1.26 line.** It was pinned below 2.0 in the same
  change that removed Selenium, which had required 2.x — so the pin outlived the conflict
  it settled and kept a 2024 release in place. Nothing here imports it, and requests is
  not the transport, so it only ever sat under the fallback path. Removed; 2.x resolves
  cleanly with no other package moving.

- **Ten sources downloaded one chapter at a time for no reason.** How many threads a
  crawler runs was derived from its requests-per-second, which is an interval and says
  nothing about how many things can be in flight — so a source that declared no rate
  limit was read as "no parallelism" and ran single-file. Thread count now comes from
  the per-site request limit instead, measured to be fastest at one thread above it:
  the spare thread stores a finished chapter while the others are fetching. Ten sources
  go from one worker to three, thirty from two, and eight drop from four or five to
  three, which measured no slower. How many jobs may run against one source at a time
  is untouched.

- **`chireads` search results had no titles.** The site moved the title out of the
  attribute the source read; it now reads the one the site actually emits.
  `totallytranslations` replaced its own HTTP session on startup, which broke every
  request it then made — that domain has since lapsed and was already flagged as
  unavailable, so this only removes the broken code.

- **Asking what is known about a site no longer records that it was asked.** Reading a
  site's diagnosis stored a profile for it, so browsing the sources list wrote one entry
  per site looked at — and with the store bounded, that could push out what a running
  crawl was relying on.

- **`lncrawl search` now ends when it says it will.** `--timeout` bounded how long
  results were collected but nothing about the requests themselves, so the command sat
  there long after the results were on screen — measured at 74 seconds for a 10 second
  timeout. A search is now treated as what it is: one throwaway question asked of many
  sites at once. It gets one attempt instead of five, no rotation, no warm-up request, no
  browser launched to solve a challenge for a session that is about to be discarded, and
  no web-archive lookup, which could never answer a search query anyway and was the
  single largest cost when archive reading was switched on. Each request is also bounded
  by the timeout the command was given. The same run now finishes in 16 seconds and
  returns *more*, because sources that used to fall outside the window now answer inside
  it. A search that ends early also says how many sources did not answer, instead of
  reporting a total failure over the results it did collect.

- **Proxies have their own screen, and each one can say what kind of address it is.**
  Reputation databases score the range an address belongs to, and only ISP, residential
  and mobile addresses get past a site that blocks on reputation — but every proxy was
  read as a datacenter address, so a residential proxy bought for exactly that purpose was
  never used for it. The crawler would give up on a block it could have cleared, then
  advise configuring a proxy that was already configured.

  Proxies were also a single line of comma-separated text holding four different
  semicolon-delimited formats, one of which nobody could be expected to remember. They are
  now a list of records — kind, address, label, on/off, and the tor-pool fields where they
  apply — edited on a Proxies screen under Settings that shows, beside each entry, whether
  it is in use, resting after a failure and for how long, and whether its kind can get past
  a reputation block at all.

  Existing configuration is imported automatically, including `PROXY_URLS` from the
  environment, and nothing needs rewriting by hand. Credentials no longer come back out of
  the API: a proxy URL's password and a tor-pool token are withheld, and leaving them
  untouched keeps what is stored.

- **A page that would not finish rendering is no longer reported as a crash.** A source
  can ask for a page to be rendered in a browser and wait for a specific element; when
  that element never appeared, the job said an unexpected error had occurred and showed a
  stack trace, which reads as a bug in the app. It is not — it means the selector does not
  match the finished page, or the page needs longer. Both that and a browser that runs a
  challenge without earning a clearance now come back as ordinary diagnoses with a remedy,
  and both count toward source health.

- **The server no longer leaks memory on every failed request.** Each API error was one
  shared exception object, created when the module loaded and raised over and over.
  Raising an exception *appends* to the traceback already on it, and a shared object is
  never collected, so every frame of every failed request stayed reachable — along with
  everything those frames' local variables pointed at. Measured: after 900 requests one
  error object held 9,000 traceback frames, and memory rose 66 MB per 800 requests with
  no ceiling. Errors are now built fresh at the point they are raised, and memory is flat
  over 6,400 requests. This also fixes a bug that was never only about memory: two
  requests failing at once shared one object, so one could be answered with the other's
  error detail.

- **Chapters stored empty before this release are recovered on their own.** Refusing to
  store an empty chapter only helps from here on; a library that already had them kept
  them forever, because nothing re-downloads a chapter already marked finished. The
  background cleanup pass now reopens them. It leaves alone the ones that were tried and
  given up on deliberately, so nothing re-enters a retry loop. `lncrawl dev
  recover-empty-chapters` still reports before it acts and can reach those too, for a
  source that has since been fixed.

- A challenge interstitial served with a `200` is no longer parsed as chapter content.
  This is the failure mode with no error to catch: the download reports success and
  stores an empty page. Sites that answer a first request with a JavaScript-only
  redirect are now followed to the real page rather than saved as a stub.

## [4.13.1] - 2026-07-25

### Fixed

- **Translator Dashboard** — Fixes dependency import in PyInstaller build

## [4.13.0] - 2026-07-25

### Added

- **In-process translation engine** — the built-in translator backends (Google/Bing/Baidu/Microsoft/Lingva) are replaced by the external `lncrawl-translator` package run in-process, giving multi-engine routing and failover managed from an admin-gated dashboard mounted at `/api/translator`. New config: a `translator.enabled` master switch to turn the feature off, plus `translator.request_timeout` and `translator.config_file`
- **Novel glossary** — a per-novel, per-language translation glossary (new `add_novel_glossary_table` migration) is sent with every request and merged back from the engine so names stay consistent across chapters; manageable via the API and kept when a translation is deleted
- **Single-volume artifacts** — `POST /api/jobs/create/make-artifacts` accepts an optional `volume` (volume serial number) to build an e-book covering just that volume; artifacts record the volume in a new `volume` column (new `artifact_volume_column` migration) and can be filtered by it via `GET /api/artifacts`. Whole-novel listings (`list_latest`/novel page/download emails) still show only full-novel artifacts
- **Per-translation delete** — remove a single language's translation of a novel without touching the others (the glossary is preserved)
- **Translated titles & volume filtering** — `list_latest`/`get_latest` support a volume filter, and the chapter/volume detail endpoints accept a `language` query param to return translated titles
- **Library favorites** — favorite a library and list favorites (new `library_favorites` migration)
- **Reading history page** — new endpoints and response models surface reading stats and continue-reading
- **Basic-tier translation** — single-novel translation jobs are available to the basic tier
- **Automatic novel language** — a novel's language is detected and set while crawling

### Changed

- **Per-source request rate limiting** — `request_concurrency` and the rate knob are merged into a single per-source `request_rate_limit`, now enforced across every concurrent job hitting a source; `FetchService` uses one scraper instance per thread
- **Resilient desktop webview startup** — startup is reworked for a smoother experience: readiness is gated on `/health`, with a fail-fast path when the server exits early and a system-browser fallback
- **Faster CLI startup** — the FastAPI import is deferred off the crawler/source import path
- **Sliding sessions** — the current session is kept alive via a refresh token on `/me`, now with an absolute cap (new `server.session_max_lifetime`, default 30 days) and role/tier re-derived from the live user on each refresh
- **Translator dashboard proxying** — proxied via base-href injection instead of URL rewriting; only the translator API is admin-gated

### Fixed

- **SMTP** — reconnect stale connections before sending mail
- **Glossary merge race** — concurrent translation jobs of the same novel no longer collide on the glossary unique constraint or drop each other's terms
- **Invite reply loop** — the incoming Subject/Message-ID reused for threaded invite replies are sanitized, so a crafted email can no longer wedge the invite handler into an endless reprocess loop
- **Artifact listing count** — the paginated total now applies the same filters as the results, fixing page counts
- **Source crawlers** — migrated many sources to the declarative `request_rate_limit` attribute

## [4.12.0] - 2026-07-14

### Added

- **Novel list filtering** — `GET /api/novels` gains sort modes (`popular`, `updated`, `created`, `chapters`, `title_asc`, `title_desc`) via a new `NovelSort` enum, backed by a `novel_popularity` migration and activity-derived popularity scoring
- **Per-novel tags** — tag attachments now live in a dedicated `NovelTag` table (new `novel_tags` migration) instead of being embedded, with supporting DAO/service changes across `tags.py`, `novels.py`, and `crawler.py`
- **CLI resume & rate limit** (#3105) — `lncrawl crawl` gains `--resume`/`--missing` to download only not-yet-crawled chapters and `--rate-limit` to throttle requests; `--resume` and `--refresh` are mutually exclusive
- **`novelarrow.com`** — new source crawler

### Changed

- **Enums stored as plain scalars** — DAO models no longer use native DB enum types; enum columns are stored as plain scalars, removing the need for Postgres enum-sync migrations (new `drop_native_enums` migration)
- **Dialect-split schema evolution** — `services/db.py` schema evolution is now split by dialect, and the SQLite DB is rebuilt from the current models while preserving data
- **Sources list not cached** — `GET /api/sources` no longer caches its response

### Fixed

- **`novelfull`** — stop downloading duplicate "half" chapters, and drop an unnecessary `soup.decompose` call in chapter-body parsing
- **Source language generation** — corrected language derivation in the sources helper

## [4.11.0] - 2026-07-09

### Added

- **Continue reading** — a new history endpoint and supporting `HistoryService` logic surface the most recent in-progress chapter so readers can resume where they left off; new response models under `server/models/history.py`
- **Library covers** — a library now displays the first available novel cover as its cover image; `LibraryService` and the library DAO/response models updated accordingly
- **Daily active users** — `GlobalActivitySummary` gains a `dau` field alongside `mau`, and admin usage is aggregated by hour with day-of-week bucketing

### Changed

- **Recommendation service** — improved recommendation logic and wiring across `recommendations.py`, `novels.py`, and `crawler.py`
- **Job dependency handling** — `FETCH_LATEST` jobs now respect dependencies; pending-job retrieval refactored (dropped the `skip_domains` parameter)
- **Activity retention** — `Scrubber` deletes `UserActivity` records older than 90 days

### Fixed

- **`lightnovelstranslations.com`** (#3067) — stop prepending the scraper origin to an already-absolute novel URL, which produced a malformed 404ing URL
- **Chapter history** — corrected chapter history addition
- **SQLAlchemy 2.0** — fixed usage list compatibility

## [4.10.0] - 2026-06-28

### Added

- **Activity heatmap** — hourly usage heatmap bucketing events by day-of-week × hour-of-day using portable integer epoch math (identical on SQLite and PostgreSQL) and shifted by a `tz_offset` query param to reflect the viewer's local time, plus additional activity-dashboard metrics — useful for spotting low-traffic deploy/maintenance windows
- **One runner per domain** — the job scheduler now guarantees a single runner processes a given domain at a time; new `job_domain` migration with supporting DAO/service logic
- **GitHub feedback** — feedback is submitted directly as GitHub issues via `utils/github.py`; the local `feedback` table is dropped (new migration)

### Changed

- **DB schema validation reworked** — schema validation now runs through `services/db.py` on startup, with a dev `migrate` command and a lint-workflow hook
- **Job runner hardening** — added a drain loop and failure safety net, consolidated queue claims, only cancels stuck jobs on runner reset, rests between iterations, and runs `gc` during scheduler reset
- **`openai` moved to a dev dependency**; CI workflows optimized
- **Updated `lncrawl-scraper`**

### Fixed

- **`freewebnovel`** (#3060) — source corrected
- Assorted cleanup and minor fixes across the crawler, binder, mail, and static-file middleware

## [4.9.0] - 2026-06-20

### Added

- **IMAP inbox listener** — `MailService` gains a start/close lifecycle and an IMAP IDLE loop (via `imap-tools`, defaults to ProtonMail Bridge on `localhost:1143`). Incoming mail from an unregistered sender automatically triggers an invite through the admin referral flow; known users are left untouched. Gated behind a new `imap_enabled` config flag (off by default); outbound mail is likewise gated behind `smtp_enabled`
- **Fetch-missing / fetch-latest jobs** — two new `JobType` values, `FETCH_MISSING` (60) and `FETCH_LATEST` (61), with dedicated handlers and `POST /api/job/create/fetch-missing` / `fetch-latest` endpoints for filling chapter gaps and pulling newly released chapters. New `sync_jobtype` Alembic migration for PostgreSQL compatibility
- **Admin activity dashboard** — `GET /api/admin/activity?type=<kind>&days=<n>` backed by four focused service methods (summary, daily active users, per-type trend, top users); new response models in `server/models/activity.py`
- **Artifact download tracking** — new `ActivityType.ARTIFACT` (12) recorded when a file under `/artifacts/` is served; other static downloads remain `DOWNLOAD`
- **Browser navigation middleware** — a `/browse/*` proxy (`BrowserNavigation`) fetches remote URLs through the scraper engine and rewrites links so navigation stays within the local server, injecting a JS interceptor that routes `fetch`/XHR/anchor clicks through the same prefix. Adds a `browse_helper` utility and an `assets/scripts` package
- **Proxy toggle** — new config option to enable/disable proxy usage in the crawler

### Changed

- **Multiple proxies supported** — proxy config reworked to accept a list of proxies; `lncrawl-scraper` bumped accordingly
- **Activity worker count** — user-activity tracking now uses `runner_concurrency` as the worker count

### Fixed

- **Active-user count** — `get_admin_summary` counted activity types instead of distinct users; replaced with a `COUNT(DISTINCT user_id)` subquery, fixing PostgreSQL compatibility
- **Sources** — updated `aquareader.net` (#3035) and `lightnovelpub.org`; regenerated source index

## [4.8.0] - 2026-06-13

### Added

- **Job notifications** — `JobNotificationService` dispatches email on job state changes (pending → running → success/failure) via a background `TaskManager`; triggered from handler helpers (`_set_running`, `_set_success`, etc.)
- **Docker healthcheck** — server container now exposes a `/health` probe

### Changed

- **Job runner refactored into typed handlers** — `JobRunner` now dispatches via a `_HANDLER_REGISTRY` of `BaseHandler`/`BatchHandler` subclasses; each job type has its own module under `scheduler/handlers/`
- **Web app synced before Docker build** — `lncrawl-web` artifacts are pulled in as part of the Docker build step
- **`crawler_version` stamped on novel/chapter updates** — upserts now use a merge strategy to preserve existing data

### Fixed

- **Server hangup** — root cause of hang addressed (event lock contention / crawler resource leak)
- **Server crash** — crawler resource leak on shutdown fixed; Docker healthcheck added
- **`crawl.py`** (#3030) — regression in CLI crawl flow corrected
- **Torproxy** — re-enabled after an unintended regression

## [4.7.0] - 2026-06-12

### Added

- **Background search jobs** — novel search is now a proper background job with two new `JobType` values:
  - `SEARCH_SOURCE` — searches a single crawlable source; trigger via `POST /api/job/create/search-sources?domain=…`
  - `SEARCH_ALL_SOURCES` — fans out across every searchable source, spawning one `SEARCH_SOURCE` child per source; idempotent on retry
  - `JobRunner` handles execution: results stored in `job.extra`, matched URLs create a `NOVEL_BATCH` child job
  - New Alembic migration (`add_jobtype`) for PostgreSQL compatibility
- **PAUSED job status** — new `JobStatus.PAUSED` enum value for finer job lifecycle control
- **Per-tier search-job rate limiting** — `BASIC` users are capped at 1 concurrent search while the general active-job quota remains independent; search query length validated (2–50 chars); results sorted by match ratio
- **NovelFire search** — `SEARCH` capability added to `NovelFireCrawler` (#3009)

### Changed

- **Removed vendored `lncrawl/cloudscraper`** — the embedded Cloudflare-bypass fork (v1/v2/v3 handlers, captcha integrations, JS interpreters, 7 913-line `browsers.json`) has been removed; HTTP scraping is now delegated to the [`lncrawl-scraper`](https://github.com/dipu-bd/lncrawl-scraper) package
- **JavaScript engine replaced**: PyExecJs → quickjs → **exejs** — lighter dependency, no Node.js or external runtime required
- **Proxy support in scraper** — the `lncrawl-scraper` integration now supports proxies; `build-essentials` added to Docker base image (#3014)
- **BrowserTemplate merged into SoupTemplate** — `BrowserTemplate` is integrated directly into the soup template hierarchy rather than being a standalone class; all browser-based sources refactored accordingly
- **Job service hardening** — event locking and improved update logic in `JobService`; request timeouts in the scraper adjusted
- **Docker improvements** — faster image builds; updated `compose.yml` and server-compose files; fixed unintended root access in `server-compose`
- **truyenfull**: updated domain and search URL; `base_url` changed to a list to support multiple domains (#3010)

### Fixed

- **Security** — path-traversal / static-file exposure vulnerability fixed in `app.py` and `staticfiles.py` (#3005)
- **katreadingcafe** — chapter link validation logic corrected to filter out non-chapter URLs (#3026)
- **Race condition** — parallel search result aggregation could yield inconsistent data under concurrent writes; fixed with proper locking
- **EPUB + NovelFire** (#2993):
  - Duplicate chapter title and serial number removed from chapter body content
  - `download_chapter_body` header extraction improved (regex + text normalisation)
  - EPUB serial heading logic refactored
- **Source loading on restart** — a failure loading one source no longer aborts the full reload cycle
- **Cover download** — full error stack trace suppressed for non-critical cover fetch failures
- **PyInstaller packaging** (`setup_pyi`) — fixed a regression in frozen-binary builds

## [4.6.0] - 2026-05-29

### New Features

- **Novel Recommendations** — the server now suggests related novels based on what you're reading
- **Machine Translation** — full translation service with multiple backends (Bing, Google, Lingva, Baidu) with automatic failover; translates chapter content, chapter titles, and artifacts (EPUB/etc.)
- **Granular translation job types** — translation tasks are now split per-resource (chapter, volume, title) instead of one monolithic `TRANSLATION` job, giving finer progress tracking
- **Referral / invite system** — users can invite others via email with a referral link
- **Expanded browser detection** — Brave, Vivaldi, Yandex, and Whale are now recognized for app-mode launching alongside Chrome/Edge
- **More supported translation languages**

### Improvements

- Browser automation migrated from Selenium to **nodriver** for more reliable JS-rendered site scraping
- Switched to a **custom caching layer** instead of `cachetools` for better control
- Announcement banners improved in the web UI
- Chapter body cleaning improved when downloading
- User activity tracking added (page visits, static file downloads)
- Webview fallback now shows just the terminal when no app-mode browser is found
- Tightened API access control; auth guards now use `Security()` instead of `Depends()`
- Removed initial content when a language is pre-defined
- Invitation email subject line updated

### Bug Fixes

- Fixed SQLite compatibility issue with migrations (`batch_alter_table`)
- Fixed Calibre-based artifact generation when using translations
- Fixed searching regression
- Fixed chapter fetch/translate functions not passing user ID correctly
- Fixed `select_descendants` typo in security module (#2966)
- Fixed invalid URL exceptions crashing `fetch_chapter` and `fetch_image`
- Fixed `ensure_load` crashing when sync thread was already cleaned up
- Fixed app startup issues

### Source Updates

- **wtr-lab.com** — multiple fixes and updates
- **novelfire.py** — several iterative fixes
- Chapter title tag removal extended to `<h4>` elements
- More sources flagged as rejected/inactive in the index

### Internal / Infrastructure

- `lncrawl-web` is no longer a git submodule; web build artifacts are bundled directly
- Removed deprecated `fetch-novel` API endpoint (replaced by `fetch-novels`)
- Python 3.15 excluded from psycopg test matrix (not yet supported upstream)
- `server-compose.yml` updated

**Full diff:** https://github.com/dipu-bd/lightnovel-crawler/compare/v4.5.0...v4.6.0

## [4.5.0] - 2026-05-20

### Bug Fixes

- Fix crash when downloading novels with more than 9 volumes ([#2970](https://github.com/lncrawl/lightnovel-crawler/issues/2970))
- Fix artifact download failing with `400 Bad Request` when filename contains `%` ([#2963](https://github.com/lncrawl/lightnovel-crawler/issues/2963))
- Fix PostgreSQL database connection broken since v4.2.1 ([#2981](https://github.com/lncrawl/lightnovel-crawler/issues/2981))
- Fix storage path directory not being created before writing URL in `_build_url`
- Add MIME type handling for file responses in the web server
- Fix browser detection on Flatpak environments

### New Features

- **Windows installer**: Added Inno Setup-based installer (`lncrawl.exe`) for proper install/uninstall on Windows
- **Fallback browser window**: When Chrome/Edge is not found, a tkinter window with the app icon is used as fallback
- **Faster Windows startup**: Switched to `--onedir` mode on Windows (vs `--onefile` on Mac/Linux) for quicker launch
- Added explicit `app` subcommand to CLI for launching the webview directly
- Improved URL building in webview server

### New Sources

- Added [novelfrance.fr](https://novelfrance.fr) ([#2946](https://github.com/lncrawl/lightnovel-crawler/pull/2946))

### Updated Sources

- Updated [wattpad.com](https://wattpad.com) ([#2983](https://github.com/lncrawl/lightnovel-crawler/pull/2983))

### Internal Changes

- Refactored LSP session management and source synchronization logic
- Enhanced LSP configuration and logging; updated dependencies
- Fixed `ruff` format command syntax in lint workflow

## [4.4.0] - 2026-05-16

### New Features

- **LSP server**: Implemented a built-in Python Language Server (`pylsp`) for source code editing, with improved readiness checks and restart logic
- **Source management API**: Added API endpoints for source code retrieval, management, and live testing directly from the web UI
- **GitHub integration**: Added GitHub token management and enhanced `GitHubClient` for fetching/editing remote source files; added remote edit link per source
- **Source testing for admins**: Admin role check and expanded source testing functionality; non-admins receive a proper error when attempting to run modified source code
- **Domain endpoint**: New endpoint to retrieve a source item by domain; `extract_host` utility for reliable domain extraction in novel creation
- **`PageSoup.prettify`**: Added `prettify` method to `PageSoup` for cleaner debug output in crawler tests
- **`dev` Makefile target**: New `make dev` target added; `watch` dependency updated
- **Pyright type checking**: Added Pyright static analysis to the lint CI workflow

### Bug Fixes

- Fixed app launch inside the webview (#2942 — also fixes webview not starting on Windows, and UV path in Makefile on Windows)
- Fixed empty chapter bodies produced by the NovelFull template
- Fixed `novelbin` and related NovelFull-based sources
- Fixed chapter list and chapter body parsing in the `novelight` source
- Fixed executor initialization in `CentralNovelCrawler`
- Fixed port extraction in `extract_host` when the port value is `None`

### Improvements

- **Faster startup**: Refactored initialization path to make CLI/server startup significantly faster
- **Chapter sync**: `ChapterService.sync` now preserves `is_done` flag and merges `extras` rather than overwriting
- **BrowserTemplate**: Fallback browser now runs in headless mode
- **TaskManager**: Refactored to manage progress bars internally; removed unused proxy module
- **EPUB metadata**: Corrected group position handling in EPUB metadata (#2905)
- **TextCleaner / Webfic**: Enhanced text cleaning and Webfic source processing
- **Crawler versioning**: Updated versioning logic; `process_info` now captures commit time
- **PR models**: Refactored PR creation models, added PR fetch endpoint, improved error handling and formatting
- **Type hints**: Improved type hint consistency across models, config, `json_tools`, and scripts
- **User index**: Optimized user index file handling
- **History limit**: Added configurable history limit to project setup

### Source Updates

- `royalroad.com` — updated (×2)
- `novelcool.com` — updated (×2)
- `freewebnovel` — updated
- `asianovel.net` — updated

### Dependency Updates

- `pyease-grpc` → `1.8.0`
- `mako` → `1.3.12` (#2950)
- Added `urllib3` version constraint
- Updated Dockerfile to sync all extras and groups during build
- Updated license metadata in `pyproject.toml`

## [4.3.1] - 2026-05-06

- Updated the version from 4.3.0 to 4.3.1.
- Modified the WebView initialization to persist cookies and storage under the APP_DIR, improving user experience and data management.

## [4.3.0] - 2026-05-06

- Refactor core components and enhance crawling functionality by @dipu-bd in https://github.com/lncrawl/lightnovel-crawler/pull/2910
- Bump mako from 1.3.10 to 1.3.11 by @dependabot[bot] in https://github.com/lncrawl/lightnovel-crawler/pull/2927
- Bump cryptography from 46.0.6 to 46.0.7 by @dependabot[bot] in https://github.com/lncrawl/lightnovel-crawler/pull/2918
- fix: fenrirealm.com crawler broken after site migration to SvelteKit by @pathsny in https://github.com/lncrawl/lightnovel-crawler/pull/2928
- fix: update skydemonorder crawler for Livewire migration by @josegonzalez in https://github.com/lncrawl/lightnovel-crawler/pull/2935
- Bump lxml from 6.0.2 to 6.1.0 by @dependabot[bot] in https://github.com/lncrawl/lightnovel-crawler/pull/2931
- Update server configuration and improve database handling
  - Changed the default server port from 8080 to 8181 in the Docker Compose configuration and server command.
  - Enhanced the database connection handling by using `engine.begin()` for transactions.
  - Updated the database schema verification method to improve clarity and logging.
  - Refactored EPUB generation logic to ensure proper item addition to the book structure.
  - Adjusted the HTML parsing logic in the Freewebnovel template for better selector usage.

## [4.2.1] - 2026-04-04

- Bump pygments from 2.19.2 to 2.20.0 by @dependabot[bot] in https://github.com/lncrawl/lightnovel-crawler/pull/2906

## [4.0.0] - 2026-03-26

### Highlights

- **Desktop:** Running `lncrawl` with no subcommand starts the **GUI (webview)** and local server by default.
- **Libraries:** Library management: create, edit, search, and browse libraries with improved UI and API support.
- **Accounts & security:** User model and verification flow simplified; **API tokens** for automation; stricter user listing and inactive-user handling.
- **Jobs & downloads:** Artifact **file sizes** tracked; job cleanup and **feedback** tooling; **content-disposition** fixes for downloads.
- **Crawling:** **Login** support on the crawl command; **list sources** output format options; site availability checks; **cloudscraper** integration refactored and updated to track upstream via a **git dependency**.
- **Sources:** Many sources updated, new indexes, and fixes across languages and templates.

### Packaging & platform

- **Python:** Project and CI target newer Python (3.12+; tooling also tracks 3.14 where applicable).
- **Dependencies:** **`uv`** is the supported way to install and sync the project (`uv.lock`).
- **Docker & CI:** Smaller images, workflow updates (e.g. Astral **uv** setup), improved release and PyPI publish flows; **PyInstaller** builds refined (including Windows **no-console** option).
- **License:** **GPLv3** (see repository license and terms/privacy docs where applicable).

### Breaking or notable changes

- **License** changed from MIT to **GPLv3** — review if you redistribute or embed the app.
- **CLI default:** No subcommand no longer “does nothing”; it **opens the GUI** — use explicit subcommands (`crawl`, `server`, `config`, etc.) for scripting.
- **Tooling:** Expect **`uv`** and updated **Makefile**/`pyproject` workflows instead of legacy `pip install -r requirements.txt` flows.
- **Scraper:** Built-in **proxy management** was removed; adjust any custom proxy setup accordingly.

### For contributors

- Linting uses **black**, **isort**, and **flake8**; `make lint` and CI align with the new layout.
- **Alembic** migrations and **artifact** schema changes (e.g. file size column) — run migrations when upgrading existing databases.

## [3.10.1] - 2025-06-16

- fix: allow downloads of all free chapters by @josegonzalez in https://github.com/dipu-bd/lightnovel-crawler/pull/2667

## [3.9.3] - 2025-06-01

- Version 3.9.3 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2653

## [3.9.0] - 2025-05-31

- Fixes Search #2649
- Version 3.9.0 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2651

## [3.8.1] - 2025-05-30

- Added source fenrirscan by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2633
- Remade Meionovel by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2635
- added source arcane translation by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2636
- added source novel543 by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2637
- rework 69shuba by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2639
- added source ranobenovel by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2643
- update source xbanxia by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2644
- added source fenrirealm by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2640
- Adds pandanovelco by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2645
- Added tags and summary to templates + new source novlov by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2638

## [3.8.0] - 2025-05-18

- Use existing template for Fenrir Translations by @kardigun in https://github.com/dipu-bd/lightnovel-crawler/pull/2545
- Fix wtr for non AI translated novels by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2565
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2566
- Fix webnovel.com source in https://github.com/dipu-bd/lightnovel-crawler/pull/2572
- Ceunovel is down by @Magos-Technicus in https://github.com/dipu-bd/lightnovel-crawler/pull/2582
- Fix NovelNext by @redowan99 in https://github.com/dipu-bd/lightnovel-crawler/pull/2595
- Fix fanmtl.com / resolve_future add exceptions by @miguelmazetto in https://github.com/dipu-bd/lightnovel-crawler/pull/2601
- fix(novelfull): remove embedded ads from chapter content by @frenicohansen in https://github.com/dipu-bd/lightnovel-crawler/pull/2609
- fix(reaperscans): update crawler by @frenicohansen in https://github.com/dipu-bd/lightnovel-crawler/pull/2612
- Add powanjuan source by @shinyPy in https://github.com/dipu-bd/lightnovel-crawler/pull/2615
- Update requests requirement from <2.30.0,>=2.20.0 to >=2.20.0,<2.33.0 by @dependabot in https://github.com/dipu-bd/lightnovel-crawler/pull/2625
- Add KatReadingCafe source. by @shinyPy in https://github.com/dipu-bd/lightnovel-crawler/pull/2626
- This updates termux by @FunMan1995 in https://github.com/dipu-bd/lightnovel-crawler/pull/2627
- Fixed Wtrlab Chapter Body by @redowan99 in https://github.com/dipu-bd/lightnovel-crawler/pull/2624
- Adding Literotica & Adding LeafStudio by @redowan99 in https://github.com/dipu-bd/lightnovel-crawler/pull/2623
- refactor: use tenacity for request retries by @frenicohansen in https://github.com/dipu-bd/lightnovel-crawler/pull/2610

## [3.7.5] - 2025-01-11

- Update mtlnovel.py by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2530
- Fixed royal road watermark issue. #2531 by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2532
- Source-Issue template change by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2536
- Fix source syosetu by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2533
- Revert "Fixed royal road watermark issue. #2531" by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2537
- Fixed royal road watermark issue by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2538
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2539
- Fix novelight.net by @kardigun in https://github.com/dipu-bd/lightnovel-crawler/pull/2535
- Add Fenrir Translations source by @kardigun in https://github.com/dipu-bd/lightnovel-crawler/pull/2540
- Add raeitranslations.com source by @kardigun in https://github.com/dipu-bd/lightnovel-crawler/pull/2542
- Add asianovel.net and wuxiasky.net sources by @kardigun in https://github.com/dipu-bd/lightnovel-crawler/pull/2541
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2547

## [3.7.4] - 2024-12-24

- Inverse invalid check by @AntonOfTheWoods in https://github.com/dipu-bd/lightnovel-crawler/pull/2410
- Add alt source for 69shuba by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2415
- Comment Removal by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2417
- add ebotnovel.com by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2419
- add ckandawrites.online by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2420
- add xnunu.com by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2421
- fix faqwiki not supporting www subdomain by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2424
- Add source 27k/乐阅读 by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2437
- Fix search for 69shuba.cx by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2438
- Correct condition when cover file does not exist by @Gilfaro in https://github.com/dipu-bd/lightnovel-crawler/pull/2448
- Add new domain name for 69shuba by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2456
- Update ddxs domain name and bad text by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2457
- Add searching for piaotian by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2455
- Added new sources by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2480
- Fixes source teanovel.com by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2478
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2485
- Generate source index by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2486
- Update VERSION by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2495
- Fix wordrain by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2496
- added novelmtl source wuxiabox.com by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2501
- added source mydramanovel.com by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2502
- Update centralnovel.py by @Magos-Technicus in https://github.com/dipu-bd/lightnovel-crawler/pull/2516
- Add wtrlab source by @divyam-gawde in https://github.com/dipu-bd/lightnovel-crawler/pull/2518
- Create novelLight by @Ankush12345567 in https://github.com/dipu-bd/lightnovel-crawler/pull/2521

## [3.7.2] - 2024-07-07

- Add source by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2388
- genesistls.com: add source crawler by @Alazari-main in https://github.com/dipu-bd/lightnovel-crawler/pull/2396
- Add source by @CxRxExO in https://github.com/dipu-bd/lightnovel-crawler/pull/2397
- Add source piaotian / 飘天文学网 by @Zokhoi in https://github.com/dipu-bd/lightnovel-crawler/pull/2393
- Rate limit 69 shuba by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2403
- Fix navigation. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2409

## [3.7.1] - 2024-05-11

- Fix novel search on empty titles by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2372

## [3.7.0] - 2024-05-11

- Add continuous navigation when arrow key is held down by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2353
- fix chinese source ddxsss by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2367
- Sort search results by amount then by similarity with input by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2364
- Version 3.7.0 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2371

## [3.6.0] - 2024-04-30

- Bug fix by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2325
- Update wtrlab.py by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2346
- Fix image fetching by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2351
- Add source by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2352
- fix chapter detection by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2360
- Version 3.6.0 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2362

## [3.5.1] - 2024-04-04

- Added url to readlightnovelorg.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2286
- add new crawler for ddxsss by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2287
- cleaner: keep HTML table structure more intact by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2292
- Core adjustments (typing, misc fixes, replacing os.path with pathlib.Path) by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2293
- URL change by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2289
- Added new sources by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2311
- Create webtoon.py by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2320
- Arabic fix by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2321
- source by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2322

## [3.5.0] - 2024-02-25

- new domain for 69shuba by @nd2024 in https://github.com/dipu-bd/lightnovel-crawler/pull/2227
- Fix source by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2230
- add tigertranslations.py as new english source by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2232
- update lightnovelreader.py URL for readlightnovel.app to readlitenove… by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2237
- add faqwiki.py as english source by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2238
- add webfic multilingual source by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2239
- fixed isotls by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2250
- Update royalroad.py by @needKVAS in https://github.com/dipu-bd/lightnovel-crawler/pull/2251
- Fix tw.m.ixdzs.com & www.aixdzs.com by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2253
- cleanup and fix 69shuba / 69shu / 69xinshu by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2256
- bato: fix empty chapters by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2257
- add new source: luminarynovels by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2258
- Fix mangabuddy chapter downloading by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2259
- QoL: Miscellanous Fixes by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2266
- Fix Syosetu and Fanstrans by @NilanEkanayake in https://github.com/dipu-bd/lightnovel-crawler/pull/2243
- add wtrlab multilingual source by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2245
- add Uukanshu (www & tw subdomains) by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2264
- add nyxtranslation as a new en source by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2268
- fix: reaperscans by @kuwoyuki in https://github.com/dipu-bd/lightnovel-crawler/pull/2277
- Add NovelDeGlace by @Vuizur in https://github.com/dipu-bd/lightnovel-crawler/pull/2278
- freewebnovel add new mirror & remove self-promo by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2281
- fix uukanshu possible failure on synopsis by @camp00000 in https://github.com/dipu-bd/lightnovel-crawler/pull/2279

## [3.4.2] - 2024-02-18

- Fix #2200 by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2203
- Added new mirror for FreeWebNovel by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2207
- Fix Calibre on macOS by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2202
- Add libxcb-cursor0 to Dockerfile by @rdonaldwilson in https://github.com/dipu-bd/lightnovel-crawler/pull/2208
- Fix wuxiaworld.com by @alzamer2 in https://github.com/dipu-bd/lightnovel-crawler/pull/2204
- Change in Termux installation manual by @pmosko in https://github.com/dipu-bd/lightnovel-crawler/pull/2248

## [3.4.0] - 2023-11-14

- Memory optimization by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2193
- A better version of PR #2155. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2196
- support single chapter volumes by @HeliosLHC in https://github.com/dipu-bd/lightnovel-crawler/pull/2051
- Fix Source by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2198

## [3.3.2] - 2023-11-01

- new domain for allnovelfull and Added New Source (daotranslate.com) by @neoryd in https://github.com/dipu-bd/lightnovel-crawler/pull/2171
- Fix source by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2173
- Fix sources and Added new sources by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2176
- Fix cannot identify image file <\_io.BytesIO by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2186
- Fix license badge on ReadMe showing Apache 2.0 when actual license is GPLv3. by @Dimi1010 in https://github.com/dipu-bd/lightnovel-crawler/pull/2184
- Version 3.3.2 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2187

## [3.3.1] - 2023-10-17

- Create rulate.py by @needKVAS in https://github.com/dipu-bd/lightnovel-crawler/pull/2086
- Update README.md by @needKVAS in https://github.com/dipu-bd/lightnovel-crawler/pull/2090
- added synopsis and tag by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2088
- Added synopsis and tags by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2087
- Update Telegram bot to python-telegram-bot 20.5 by @pmosko in https://github.com/dipu-bd/lightnovel-crawler/pull/2092
- fix: removed wuxiaclick by @wuxmes in https://github.com/dipu-bd/lightnovel-crawler/pull/2085
- Syosetu volume error fix by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2083
- Added synopsis and fixed author by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2141
- fix author by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2145
- novel-bin.net by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2139
- Fix source by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2147
- Update novelgate url by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2158
- Fix PDF exporting with docker by @rdonaldwilson in https://github.com/dipu-bd/lightnovel-crawler/pull/2150
- Fix jaomix.py -> error No chapters found by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2148
- Fixed "No chapters found" error in two sources by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2161
- New option and source by @CryZFix in https://github.com/dipu-bd/lightnovel-crawler/pull/2167
- Version 3.3.1 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2168

## [3.3.0] - 2023-09-08

- Dropped support for python 3.7
- Fix chrysanthemumgarden by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2066
- Fixed Freewebnovel by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2068
- Update novelsemperor.py by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2070
- 1stkissnovel fix by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2080
- Headers not passing to get_soup fixed. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2079
- Updated the source URL for the Chinese content from '69shu' to '69shuba' by @Aeterno8 in https://github.com/dipu-bd/lightnovel-crawler/pull/2075
- Fix for Calibre PDF generation. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2081
- Version 3.3.0 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2084

## [3.2.10] - 2023-08-27

- Fix ranobes, switch to browser on bot detection by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2050
- Create ranobelib.py by @needKVAS in https://github.com/dipu-bd/lightnovel-crawler/pull/2044
- Update chrysanthemumgarden.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2042
- source file by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2060
- Fix to work on Chrome116 with undetected-chromedriver 3.5.3 by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2054
- Ratelimiting in taskmanager by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2053
- Use chardet by default to find the encoding by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2040
- Add source Xbanxia. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2061
- Fixing Novelgate source. by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2062

## [3.2.9] - 2023-08-18

- HOTFIX for scribblehub browser search blocking search progess by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2013
- Hottfix: scribblehub by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2016
- Move Docker image from 11 to 12 (Bullseye to Bookworm) by @maroney-tm in https://github.com/dipu-bd/lightnovel-crawler/pull/2018
- Create 69shu.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2022
- new url lightnovelreader.app by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2024
- Create wuxiaclick.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2026
- Create engnovel.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/2028
- Solve source 1stkissnovel.org issue by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2032
- fixed source by @ismaelcompsci in https://github.com/dipu-bd/lightnovel-crawler/pull/2034
- Fix undetected_chromedriver version issue #2035 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2036
- Fixed infinitetrans source by @zGadli in https://github.com/dipu-bd/lightnovel-crawler/pull/2043
- Version 3.2.9 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2037
- Update freewebnovel.py by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2047

## [3.2.8] - 2023-07-21

- fix: calibre binder by @kuwoyuki in https://github.com/dipu-bd/lightnovel-crawler/pull/2003
- Rewrite for lightnovels.me by @Seven0492 in https://github.com/dipu-bd/lightnovel-crawler/pull/1993
- Update mixednovel.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1997
- Update readwn.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1996
- new url by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/2000
- lightnovelheaven synopsis and tag support by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1998
- Feature novelhallcom rewrite by @Seven0492 in https://github.com/dipu-bd/lightnovel-crawler/pull/1999
- Some options seems deprecated in selenium by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1991
- Fixed typo in ReadWNCrawler by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2007
- Rewrite scribblehub.com with browser by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1992
- Rewrite for ranobes.top using browser by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1990
- Fix NovelMTLTemplate for single page chapter list by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/2006
- Version 3.2.8 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/2012

## [3.2.7] - 2023-07-01

- Fix for bestlightnovel and a new source anime-sama.fr by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1945
- Fix indowebnovel info and list chapters by @yogasw in https://github.com/dipu-bd/lightnovel-crawler/pull/1949
- Update sources by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1950
- Add source skydemonorder by @ismaelcompsci in https://github.com/dipu-bd/lightnovel-crawler/pull/1959
- add novelku.id by @yogasw in https://github.com/dipu-bd/lightnovel-crawler/pull/1967
- Update sources by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1968
- Fix typo by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1977
- Update 1stkissnovel.py domain has changed from .love to ,org by @Anuj2976 in https://github.com/dipu-bd/lightnovel-crawler/pull/1978
- Fix exiledrebels.py by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1980
- fix for lightnovelstranslations.com/ by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1988
- Fix for lightnovelpub.com by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1986
- fix for novelsemperor.com by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1987
- Fix chireads by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1985
- Browser for https://novelsonline.net by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1984
- Update sources and fix an issue in crawler template by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1989

## [3.2.6] - 2023-04-10

- Rename novel_language => language by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1936
- Version 3.2.6 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1937

## [3.2.5] - 2023-04-09

- Improve image download by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1929
- Fix PDF conversion not working #1931 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1932
- Version 3.2.5 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1933

## [3.2.4] - 2023-04-07

- Fix base url lightnovelreader by @mesmerlord in https://github.com/dipu-bd/lightnovel-crawler/pull/1860
- Fix for Novelpub template browser by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1865
- Added language, synopsis and tags support by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1869
- Better Fix for Novelpub by @zerty in https://github.com/dipu-bd/lightnovel-crawler/pull/1872
- pandanovel.org by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/1878
- freewebnovel by @SirGryphin in https://github.com/dipu-bd/lightnovel-crawler/pull/1877
- Fix 'jaomix' and 'mangastic' source by @watzeedzad in https://github.com/dipu-bd/lightnovel-crawler/pull/1875
- Fix sources & add language + tags list by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1880
- Create kolnovel.py by @Dark6ness in https://github.com/dipu-bd/lightnovel-crawler/pull/1899
- Update python-dotenv requirement from <1.0.0,>=0.15.0 to >=0.15.0,<2.0.0 by @dependabot in https://github.com/dipu-bd/lightnovel-crawler/pull/1901
- Update python-slugify requirement from <8.0.0,>=4.0.0 to >=4.0.0,<9.0.0 by @dependabot in https://github.com/dipu-bd/lightnovel-crawler/pull/1876
- fix empty JSON file error by @zimorok in https://github.com/dipu-bd/lightnovel-crawler/pull/1903
- Fix 'royalroad' source novel title and author by @Dimi1010 in https://github.com/dipu-bd/lightnovel-crawler/pull/1902
- fix: royalroad by @kuwoyuki in https://github.com/dipu-bd/lightnovel-crawler/pull/1904
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1915
- Added synopsis to epub metadata by @OtterVersion in https://github.com/dipu-bd/lightnovel-crawler/pull/1920
- Dev by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1922
- Beautymanga has a new url by @jere344 in https://github.com/dipu-bd/lightnovel-crawler/pull/1928
- Fix selenium unable to connect to chrome in headless mode by @watzeedzad in https://github.com/dipu-bd/lightnovel-crawler/pull/1926
- 3.2.4 by @dipu-bd in https://github.com/dipu-bd/lightnovel-crawler/pull/1930

## [3.2.0] - 2022-12-09

- Adds NovelUpdates templates
- Unknown sources will use NovelUpdates as a Fallback
- Drops support for python 3.6
- Using undetected-chromebrowser as default
- Auto parse unknown sources

## [3.0.0] - 2022-10-08

Major changes in this release:

- Selenium based browser to bypass cloudflare protection
- Template support for extending the base crawler
- Lookup bot to find a template for new novel sources.
- Models for Chapter, Volume, Novel etc.
- Volume list is now optional for crawlers
- Styling updates for epub
- Minify HTML to reduce epub size
- Improve and enhance the cleaner
- Fixes a lot of sources, including webnovel
- New sources

## [2.34.0] - 2022-09-08

- Update sources
- Enable proxy only when `--auto-proxy` is passed
- Fix post request
- Discard failed images
- Use GoFile for bots

## [2.33.0] - 2022-08-26

- Enables auto proxy switching every 30s with [free-proxy](https://pypi.org/project/free-proxy/)
- Fixes download error reporting that was causing crash
- Makes the final URL input optional for the `--page` option #1161
- Fixes Change Selection not working when input argument is present
- Fixes and adds new sources

## [2.32.0] - 2022-08-20

- Refactors downloader to download images and chapters more efficiently
- Updates for a lot of sources
- Supports images for web format
- Improves images in epub
- Updates user agents
- Handle no chapter and volumes with an exception
- Re-enable 403 Forbidden message
- Dependency updates

## [2.31.0] - 2022-05-14

- Add and update sources.
- Enable login to wuxiaworld.com: https://github.com/dipu-bd/lightnovel-crawler/discussions/1360

## [2.29.0] - 2022-01-29

- Made novel search faster
- Retry on novel download failure in console bot (for searched novels)
- Fixes a few source issues

## [2.28.9] - 2021-10-15

- Reduces cover image size
- New structure in sources
- Updates rejected source list
- Updates and fix sources
- Changes user agents in scraper
- Adds gofile upload support in bots

## [2.27.1] - 2021-07-26

- [Suggestion] Let us test using a local crawler file #843
- Error: 'charmap' codec can't decode byte 0x90 #882

## [2.26.5] - 2021-07-11

- trying to fix 'chapmap' issue

## [2.26.4] - 2021-07-11

- fixes a lot of issues
- adds new sources

## [2.26.2] - 2021-05-08

- Fix startup issue
- Downgrade `cryptography` version to solve issue with rust build on old pip
- Fix always showing delete output folder confirmation

## [2.26.0] - 2021-05-06

- Download images from chapter contents #850
- Use the meta file if available to resume download #611
- Enables login on babelnovel
- Add new sources and fix sources
- Add a banner

## [2.25.1] - 2021-04-25

- 10+ new sources
- Filter out sources to search
- Bug fixes for several sources
- Discard support for python 3.5

## [2.24.5] - 2021-02-17

- Fix some minor bugs
- Update requirements

## [2.24.3] - 2021-02-12

- Adds new source
- Fixes bug
  #733

## [2.24.1] - 2020-12-14

- Fix issue #691 #692

## [2.24.0] - 2020-12-13

- Support python 3.9
- Replace pyinquirer with questionary
- Fix sources

## [2.22.1] - 2020-06-24

- Fix issue #512
- Add two new sources:
  - `https://jpmtl.com/`
  - `https://mangatoon.mobi/`

## [2.22.0] - 2020-06-17

- Move `src` to `lncrawl` for ease of use with pipenv
- Upgrade dependencies
- Fixes for a lot of sources thanks to @Epicpkmn11 @kuwoyuki @dipu-bd
- Get credential file and folder-id for gdrive from .env

## [2.21.0] - 2020-05-05

- Sources:
  - [novelsrock] Re-enable it and fix some issues
  - [boxnovel] Fix for novels without images #401
  - [wuxiasite] Fix image src #397
  - [wordexceprt] Fix chapter parsing #397
  - [anythingnovel] Disable it. Reason: Site broken #397
  - [rebirthonline] disabled. site moved
  - [wuxiaco] fix crawler
  - [novelfull.com] Add https base url
  - [wuxiacom] Fix searching
  - [fu_kemao] fix
  - [lnmtl] Fix volume list parsing
  - [novelraw] Fix title parsing
  - [novelfull.com] Add https base url
  - [mtled-novels] removed
- bots:
  - [discord] Remove async from cleanup_handlers
  - [discord] Update messages
  - [discord] Fix random.choice call
  - [discord] Use file logger
  - [discord] handle and report error more
  - [discord] fix linting issue on python 3.5
  - [discord] Reenable search on discord
  - [discord] Discover signal char more simply
  - [discord] save logs with shard id
  - [discord] Improve distributed processing
  - [test] Catch cloudscraper exceptions
  - [test] Add more test input

## [2.20.0] - 2020-03-23

- Update crawlers:
  - Delete comrademao.py and Remove all comrademao keywords #360 #361 #362
  - [machinetrans] Improve chapter body parsing #364
  - [mtled] disable search for cloudflare issue #365
  - [lnmtl] Fix bad volume number issue #366
  - [wuxiaworld.com] Fix Error: 'NoneType' object has no attribute 'text' #371
  - [wuxiacom] Fix title for wuxiacom crawler #382
- Bot update:
  - Fix and refactor discord bot #367 #369
  - [discord] Handle destroying more elegantly #370
  - [telegram] Only upload file to google drive when size exceeds 50mb #377
  - [discord] Cleanup handlers older than 1 day #377
  - [discord] Disable search & improve public folder access #377
  - [telegram] limit available formats #377
  - [discord] Look for novel url input at the beginning #377
  - [discord] Do not delete output folder at exit #377
  - [discord] Fix startup issue #378
  - [discord] Quote download link #380
  - [discord] Do not quote the whole url, only the filename #381
- Other updates:
  - [binders] Skip empty chapter or display no contents message #364
  - Replace cfscrape with cloudflare #365
  - Use cloudscraper in update_checker #367
  - Compress single formats together only #377

## [2.19.5] - 2020-03-04

- Bug fixes: #355
  - [lnmtl] Fix chapter numbering issue #345
  - [gravitytales] Fix chapter list and body parsing
  - Show cairosvg import error as info
- [wuxiacom] Fix chapter missing title issue #356
- Disabled search: scribblehub, wuxiasite for cloudflare issue #353
- [discord-bot] Put archives to public data if available #352

## [2.19.4] - 2020-02-25

- Bug Fix: Add pillow to `requirements.txt`

## [2.19.3] - 2020-02-23

- Update cfscrape to 2.1.1
- [novelringan] Fix duplicate body
- Fix setup_pyi
- Remove cairosvg from requirements.txt
- Install cairosvg as optional inside build script

## [2.19.2] - 2020-02-15

- New sources:
  - `https://rewayat.club`
  - `http://boxnovel.org` with search capability. @Sakari Saastamoinen
  - `https://www.worldnovel.online/`
- Remove sources:
  - `https://www.flying-lines.com`: Obfuscated content
  - `https://novelsrock.com`: 404 - Not Found
- Fix sources:
  - Remove all prettify
  - [royalroad] Clean contents
  - [royalroad] Fix search
  - [test] Update www.tiknovel.com input
- Replace download links for windows and linux standalone
- [.travis.yml] check syntax before running script
- [crawler] Fix removing the next <br> tags
- [test bot] reverse format, update inputs and tests
- Enable specifying text direction in crawler
- Fix binders/web.py
- Use GITHUB_TOKEN instead of password for posting issue from test bot

## [2.19.1] - 2020-01-07

- New source: <http://tiknovel.com>
- [listnovel] fix title parsing
- [novelfull] Fix get chapter list on non-paginated links
- [.appveyor] add --no-cache-dir to install
- [test/post_github] Fix strftime format specs

## [2.19.0] - 2020-01-06

- **Breaking Change**
  - Move folder `src/spiders` to `src/sources`
  - Auto import all spiders in `src/source/__init__.py`
  - To add new source, no need to update `__init__.py` file from now on, just provide `base_url` property to the subclass of the `Crawler` you have created. It can be a string or an array of strings. See existing sources in `src/sources/` folder for example.
  - [sources/_template.py] -> update comments
- New sources:
  - `tomotranslations.com`
  - `https://4scanlation.com/`
  - `http://www.tiknovel.com/`
  - `https://listnovel.com`
  - `https://www.wuxialeague.com/`
  - `http://liberspark.com`
  - `https://webnovelindonesia.com`
- Disabled or removed sources:
  - `https://myoniyonitranslations.com/`
  - `https://www.jieruihao.cn/`
- Feature updates:
  - [console] by default only generate epub format
  - #283 Feature request: Adding Chapter Count To Volume
- Bug fixes:
  - fix gravitytales parsing bug 282 @diogenes895
  - fix content select for wuxiasite @diogenes895
  - [webnovel.com] Chapters in "Table of Contents" isn't numbered
  - [gravitytales] fix content formatting
  - [wuxiasite] keep old style chapter content recognizer, just in case
  - [translateindo] remove unwanter characters from author name
  - [worldnovelonline] Disable search cause it takes too long to respond
  - [wuxiaco] update base url
  - [test bot] Ignore HTTPError (do not report them to issues)
  - [test-bot] define output formats manually
- Updates to test bot
  - [test] change how to process errors
  - Add or update more inputs in test_inputs.py
  - [test bot] from requests import ConnectionError
- [setup_pyi.py] Use hidden import spec for src/sources
- Create scripts folder for publish scripts
- [crawler.py] Add `verify=False` and `timeout=2.5 minutes` for `get_response`
- [requirements.txt] Bump version: beautifulsoup4, js2py

## [2.18.0] - 2019-12-24

- New sources:
  - <https://www.aixdzs.com>
  - <https://webnovelonline.com>
- Fixed or updated sources:
  - [mtled-novels] Add support for login
  - [webnovel] Remove pirate text
  - [creativenovels] clean up nag spans and style tagbarf @tidux
  - [wuxiacom] ul-tags used for dialogue removed by crawler
  - [wuxiacom] dialogue missing line breaks
  - [zenithnovels] fix chapter list ordering
  - [qidiancom] fix: get volume list from ajax call
- Bots:
  - [test] Refactoring
  - [test] Changed test inputs for some sources
  - [console] fix: some arguments are not showing in help
  - [console] Add two more argument options:
    - `--filename NAME`: Set the output file name
    - `--filename-only`: Skip appending chapter range with file name
- Testing: Update .travis.yml, .appveyor.yml to support for python 3.8
- Raise error if response status code is not 200 in crawler.py
- Remove useless logging from novel-info in most crawlers
- Raise a ConnectionError on improper html document
- Update chapter and volume title: do not set default title unless empty

## [2.17.1] - 2019-12-08

- New sources:
  - https://novelringan.com/ #252 @yudilee
  - https://wuxiaworld.site/ #251 @yudilee
  - https://kiss-novel.com/ #240 @yudilee
- Updated sources:
  - [readln] Do not display unncessary exceptions
  - [creativenovels] Extract the security key for chapter list
  - [kisslightnovels] Remove badge from title
  - [babelnovel] Do not display limited free chapters in for now
  - [webnovel] Fix content formatting
  - [readnovelfull] Parse old style chapter content
  - [babelnovel] Ignore error if no cssUrl is available
- Remove sources:
  - [jieruihao] Site no longer available
- Add tests for kiss-novel and machine-translation

## [2.17.0] - 2019-12-03

- New sources:
  - <https://ranobelib.me/> @juh9870
  - <https://www.flying-lines.com/>
- Fix Heroku:
  - Added Calibre ebook and node buildpack @NNTin
  - Added required package.json
  - Fix: mkdir threw error when already exists
- Bot updates:
  - [console] Enable output choice and use list instead of confirm
  - [discord] Enable multiple format choosing
- Fix sources:
  - [babelnovel] Recognize limited free novel chapters
  - [webnovel] Hide locked chapters and fix chapter download
  - [babelnovel] Fix issue with url @yudilee
  - [readnovelfull.com] Fix get chapter body @yudilee
  - [worldnovelonline] Get chapter list in chunk of 100 @yudilee
  - [creativenovels ] fix chapter listing @tidux
  - [machinetransorg] minor fix @yudilee
- Refactoring:
  - Split bot/console.py into multiple parts
  - Rename method: bind_books -> generate_books
- Fix `cfscrape` @yudilee
- Fix test.py

## [2.16.2] - 2019-11-10

- New sources:
  - https://id.mtlnovel.com/
  - https://www.shinsori.com/
- Fix fanfiction
- Add text_unidecode resource with setup_pyi
- Use win_unicode_console to fix #214

## [2.16.1] - 2019-10-26

- New sources:
  - `www.machine-translation.org`
  - `www.fanfiction.net`
  - `www.mtlnovel.com`
  - `wordexcerpt.com`
  - `translateindo.com`
- Fix `https://worldnovel.online`
- [babelnovel] Remove locked chapters from listing
- Convert downloaded cover into png before saving
- Upgrade requirements.txt

## [2.16.0] - 2019-10-17

- Add new crawler: `https://www.qidian.com/` (chinese)
- Fix 8 crawlers: babelnovel, kisslightnovel, worldnovel.online, novelfull, wuxiacom, gravitytales, tapread, rebirthonline.
- Improvement of console argument parser
- Heroku deployment support
- Add tests for some crawlers
- Minor housekeeping and formatting
- Add boolean field `title_lock` with volume items to not format the volume title with default formatter.
- Add boolean field `title_lock` with chapter items to not format the chapter title with default formatter.
- Add boolean field `body_lock` with chapter items to not format the chapter body with default formatter.

## [2.15.1] - 2019-09-22

- Fix console-bot issue with novel-url recognition

## [2.15.0] - 2019-09-21

- Fix chapter range selection
- New source: **novelonlinefull**
- Fix babelnovel, tapread, & webnovelonline
- Display rejected source warning
- Remove cairosvg exception at loading
- Update argument list to console bot
- Add new argument: `list-sources` to list all supported sources
- Minor update to test-bot

## [2.14.2] - 2019-08-30

- [crawler.py] Add method: is_relative_url
- Add all racovimge templates
- Fix racovimge templates that cause cairosvg to crash
- Fix 4scanlation
- Change html_style loader and minifier
- Update issue templates
- Fix setup_pyi and update version
- Removed yukinovel.id

## [2.14.1] - 2019-08-27

- Add cairosvg data files to fix standalone package
- Remove some italic illegible fonts
- Improve and cleanup download and generate cover
- [test] Add worldnovel.online to ignore list

## [2.14.0] - 2019-08-24

- [display] Add linux bundle link on `new_version_news`
- Fix jinja2 template loader path (cover image generator)
- Add source: https://kisslightnovels.info
- [console bot] Add a back button in novel selection
- [console bot] Add change range selection option
- Remove prev-next chapter nav in wuxiacom
- [epub] Change cover image size
- [downloader] Remove volume title from chapter body
- [calibre] Add header template for pdf
- New option: `--add-source-url` to append source url at the end of each chapter

## [2.13.6] - 2019-08-20

### Changes since 2.13.0

- Add https://www.asianhobbyist.com
- Add `noscript` tag to `bad_tags` in `crawler.py`
- Add source url at the end of each chapters
- Improve update checker
- Create local copy of racovimge to resolve dependencies in pyinstaller
- Remove dependency `racovimge` and degrade `python-slugify`
- Remove some problematic templates of `racovimge`
- Use stable version of pip in publish
- Update setup scripts to clear build errors

## [2.13.0] - 2019-08-16

### Changes

- Fix volume title taking a single page
- Fix bot api file upload limitation error message
- Fix binder issue of modifying output_formats
- Fix meinovel crawler
- Add new crawler for jieruihao.cn
- Fix yukinovel.me
- Fix m.romanticlovebooks.com
- Add cairosvg dependency to generate cover image
- Add test for www.jieruihao.cn
- `[crawler.py]` Remove pirate tag in clean_contents
- Update cfscrape
- Improve error logging
- Remove old binders

## [2.12.1] - 2019-08-13

- Remove novelgo.id
- Fix binders

## [2.12.0] - 2019-08-12

- Use CALIBRE to convert epub to other output formats
- Fix webnovel by removing unknown tag
- Add source: novelgo.id

## [2.11.1] - 2019-08-03

Changes since 2.11.0:

- Fortify `discord.py` against sudden crash related to session issues.
- Add source: https://www.wattpad.com/
- Fix source: https://babelnovel.com/
- `[novel_search.py]`: Cleanup and finish progressbar when done.

## [2,11.0] - 2019-07-13

- Upgrade discord bot.
- Use `recovimge` as fallback to generate cover.
- Cleanup progress bar on finish.
- Improve setup and publish script to support all platforms.
- Clean chinese texts from novel contents.
- Remove chapter and volume list logs from novel info
- Add new crawler: rebirthonline
- `[novelfull]` Call clean_contents on chapter body.

## [2.10.1] - 2019-06-29

- Removed `comrademao`, on request of the owner.

## [2.10.0] - 2019-06-23

```
- Rename source folder `lncrawl` -> `src`
- [babelnovel] Clean mumbo contents
- [creativenovels] Fix empty body
- [romanticlovebooks] Fix chapter body
- Add source: https://light-novel.online/
- Fix telegram bot cannot show progress
- Make automated bug report from test-bot
```

## [2.9.13] - 2019-06-15

- Fix crawler: babelnovel
- Fix crawler: novelall

## [2.9.0] - 2019-03-15

- A lot of bug fixing
- Whole new search feature
- New sources

## [2.7.12] - 2019-02-14

- Bug fixing
- New sources

## [2.6.4] - 2019-01-09

### Changes since 2.6.0

- Added support
  - http://fullnovel.live/
  - https://www.novelall.com/
- Fix login issue for LNMTL
- Fix chapter number parsing for LNTML
- Change app directory structure
- Remove tests (temporary)
- Add argument: `--suppress` to supress all outputs
- Add argument: `--output` or `-o` to get **output path**
- Fix `extract_contents` in file: `crawler.py`

## [2.6.0] - 2018-12-10

### Changes since 2.5.10

- Implement **novel searching**
- Fix lnindo
- Fix boxnovel's title and image parser
- Raise exception on unrecognized url instead of exiting directly

## [2.5.10] - 2018-12-05

### Changes from 2.5.0

- Add new sites:
  - https://webnovel.online
  - https://romanticlovebooks.com
  - https://m.wuxiaworld.co
  - https://m.wuxiaworld.com
- Add auto update checker
- Display an error message if the app stops by an Exception.
- Fix volume title parsing issue with LNMTL
- Separate assets and convert them to python script before publishing
- `crawler.py`: Use 1 based indexing in `get_chapter_index_of`
- Some minor bug fixing

## [2.5.0] - 2018-12-02

### Changes since 2.4.1

- Add an argument parser. Access it by, `lncrawl -h`
- Add an **INTRO** page to _epub_ and _mobi_
- Enable **HTML** binding with progress percentage
- Source input choice is _not necessary_ anymore
- Use 1 based indexing in `Crawler.get_chapter_index_of`
- Keep track of last visited URL
- A lot of fixing and refactoring
- Supports WINDOWS now

## [2.4.1] - 2018-11-29

### Changes since 1.4.0

- Rename project to **Lightnovel Crawler** everywhere.
- New sources: **Boxnovel**, **NovelPlanet**, **Idquidian**, **lnindo**, **WuxiaWorldOnline**
- New output: **Text**
- Created a new interactive prompt.
- Improve crawling and binding process
- Create a template Crawler object
- Improve chapter title and body parser
- _Download kindlegen only when necessary_
- Do not pack by volumes by default
- Force UTF-8 encoding of response
- And many more small improvements

## [1.4.0] - 2018-09-04

Changes from v1.3.3

- Fix chapter indexing problem

## [1.2.4] - 2018-07-20

### Changes

- Fixed KindleGen not working on Windows
- Fix help info

## [1.2.3] - 2018-07-17

### Fixes

- Fixed error caused by invalid symbols

[4.10.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.9.0...v4.10.0
[4.9.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.8.0...v4.9.0
[4.8.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.7.0...v4.8.0
[4.7.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.6.0...v4.7.0
[4.6.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.5.0...v4.6.0
[4.5.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.4.0...v4.5.0
[4.4.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.3.1...v4.4.0
[4.3.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.3.0...v4.3.1
[4.3.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.2.1...v4.3.0
[4.2.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v4.0.0...v4.2.1
[4.0.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.10.1...v4.0.0
[3.10.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.9.3...v3.10.1
[3.9.3]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.9.0...v3.9.3
[3.9.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.8.1...v3.9.0
[3.8.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.8.0...v3.8.1
[3.8.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.7.5...v3.8.0
[3.7.5]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.7.4...v3.7.5
[3.7.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.7.2...v3.7.4
[3.7.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.7.1...v3.7.2
[3.7.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.7.0...v3.7.1
[3.7.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.6.0...v3.7.0
[3.6.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.5.1...v3.6.0
[3.5.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.5.0...v3.5.1
[3.5.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.4.2...v3.5.0
[3.4.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.4.0...v3.4.2
[3.4.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.3.2...v3.4.0
[3.3.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.3.1...v3.3.2
[3.3.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.3.0...v3.3.1
[3.3.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.10...v3.3.0
[3.2.10]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.9...v3.2.10
[3.2.9]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.8...v3.2.9
[3.2.8]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.7...v3.2.8
[3.2.7]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.6...v3.2.7
[3.2.6]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.5...v3.2.6
[3.2.5]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.4...v3.2.5
[3.2.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.2.0...v3.2.4
[3.2.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v3.0.0...v3.2.0
[3.0.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.34.0...v3.0.0
[2.34.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.33.0...v2.34.0
[2.33.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.32.0...v2.33.0
[2.32.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.31.0...v2.32.0
[2.31.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.29.0...v2.31.0
[2.29.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.28.9...v2.29.0
[2.28.9]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.27.1...v2.28.9
[2.27.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.26.5...v2.27.1
[2.26.5]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.26.4...v2.26.5
[2.26.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.26.2...v2.26.4
[2.26.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.26.0...v2.26.2
[2.26.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.25.1...v2.26.0
[2.25.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.24.5...v2.25.1
[2.24.5]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.24.3...v2.24.5
[2.24.3]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.24.1...v2.24.3
[2.24.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.24.0...v2.24.1
[2.24.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.22.1...v2.24.0
[2.22.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.22.0...v2.22.1
[2.22.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.21.0...v2.22.0
[2.21.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.20.0...v2.21.0
[2.20.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.5...v2.20.0
[2.19.5]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.4...v2.19.5
[2.19.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.3...v2.19.4
[2.19.3]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.2...v2.19.3
[2.19.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.1...v2.19.2
[2.19.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.19.0...v2.19.1
[2.19.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.18.0...v2.19.0
[2.18.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.17.1...v2.18.0
[2.17.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.17.0...v2.17.1
[2.17.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.16.2...v2.17.0
[2.16.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.16.1...v2.16.2
[2.16.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.16.0...v2.16.1
[2.16.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.15.1...v2.16.0
[2.15.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.15.0...v2.15.1
[2.15.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.14.2...v2.15.0
[2.14.2]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.14.1...v2.14.2
[2.14.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.14.0...v2.14.1
[2.14.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.13.6...v2.14.0
[2.13.6]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.13.0...v2.13.6
[2.13.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.12.1...v2.13.0
[2.12.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.12.0...v2.12.1
[2.12.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.11.1...v2.12.0
[2.11.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2,11.0...v2.11.1
[2,11.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.10.1...v2,11.0
[2.10.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.10.0...v2.10.1
[2.10.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.9.13...v2.10.0
[2.9.13]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.9.0...v2.9.13
[2.9.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.7.12...v2.9.0
[2.7.12]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.6.4...v2.7.12
[2.6.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.6.0...v2.6.4
[2.6.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.5.10...v2.6.0
[2.5.10]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.5.0...v2.5.10
[2.5.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v2.4.1...v2.5.0
[2.4.1]: https://github.com/lncrawl/lightnovel-crawler/compare/v1.4.0...v2.4.1
[1.4.0]: https://github.com/lncrawl/lightnovel-crawler/compare/v1.2.4...v1.4.0
[1.2.4]: https://github.com/lncrawl/lightnovel-crawler/compare/v1.2.3...v1.2.4
[1.2.3]: https://github.com/lncrawl/lightnovel-crawler/releases/tag/v1.2.3
