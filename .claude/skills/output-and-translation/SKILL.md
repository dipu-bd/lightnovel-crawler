---
name: output-and-translation
description: Binder (e-book output formats) and the Translation service — architecture and recipes for adding an output format or changing how novels are translated. Use when working in services/binder/ or services/translators.py.
---

# Binder (`lncrawl/services/binder/`)

A dispatch table `archive_maker: Dict[OutputFormat, Callable]` in `service.py` maps each
format to a builder. EPUB, JSON, and text have native builders; every other format is
`convert_epub` — Calibre converts **from a previously built EPUB artifact** (it raises
`ServerErrors.no_epub_file` without one). `available_formats` derives from Calibre
availability: without Calibre only the native formats exist. Zip-emitting builders are listed
in `requires_zip`.

**Builder contract** (all builders): `def make_x(working_dir: Path, artifact: Artifact,
signal=Event(), **kwargs) -> None` — write to a temp file inside `working_dir`, then
atomically replace `ctx.files.resolve(artifact.output_file)`. Poll `signal.is_set()` and raise
`AbortedException` for cancellation. `make_artifact` owns the Artifact row, temp-dir lifecycle,
and cleanup.

**Calibre** (`calibre.py`) has two paths: a remote convert API (posted through
`ctx.http.session(signal)`) and the local `ebook-convert` executable, with configurable
fallback. Options are built backend-agnostic as `(flag, value)` tuples and rendered per path.

**Recipe — new output format**:
1. Add the value to `OutputFormat` in `lncrawl/enums.py` (string enum; note name ≠ value is
   allowed, e.g. `text` → `"txt"`). Enum changes need a Postgres enum-sync migration — see the
   `db-migration` skill.
2. Register it in `archive_maker`. If Calibre supports the extension, point it at
   `convert_epub` (one line); otherwise write a builder following the contract (add to
   `requires_zip` if it emits a zip).
3. Nothing else: `available_formats` and the API derive from the enum + table. Per-tier
   format gating is separate (`ctx.tier.enabled_formats`).

**Files**: `ctx.files` (`services/file.py`) resolves artifact-relative paths under the app
data dir, writes atomically, and transparently gzip-compresses text — chapter content on disk
is compressed; always read it via `ctx.files.load_text(...)`.

# Translation (`lncrawl/services/translators.py`)

Translation runs **in-process** via the external `lncrawl-translator` package (imported as
`translator`; sibling repo). `ctx.translator` (`TranslationService`) owns the glossary loop
and persistence; the package owns engines, routing lanes, rate limits, retries, and failover.

- **`ctx.translator.engine`** — a lazily constructed `translator.TranslatorService`: a sync
  facade running the async engine router on its own event-loop thread. Its YAML config path
  comes from `ctx.config.translator.config_file` (app data dir); engines/keys/routing are
  edited through the mounted dashboard, not lncrawl settings. `close()` is guarded in
  `ctx.destroy()`.
- **Dashboard** — the package's web UI is mounted at `/api/translator` by an admin-gated
  ASGI wrapper (`server/api/translator.py`, `TranslatorDashboard`): Bearer/`?token=`/cookie
  auth, token→cookie redirect dance, trailing-slash enforcement. It is a raw ASGI mount —
  app-level exception handlers and router security do NOT apply inside it.
- **Calls** — `_translate_texts`/`_translate_html` build request dicts and go through
  `_invoke`, which maps package errors to `ServerErrors`: `ApiError` 503 →
  `translation_quota_exhausted`, other `ApiError`/`ValidationError` → `translation_failure`,
  facade `AbortedError` → `AbortedException`. The job `signal` and
  `ctx.config.translator.request_timeout` are passed to every engine call.
- **Glossary loop** — `translate_novel/volume/chapter` load the stored `NovelGlossary`,
  send it with each request, and merge returned `new_terms` back. Chapter translation
  dedupes via a content hash and stores results through `ctx.files.save_text`.
- **Detection** — `ctx.translator.detect_language(text)` (local, no quota, no event loop)
  returns an ISO 639-1 code or None. `fetch_novel`/`fetch_chapter` use it to fill
  `Novel.language` when the source doesn't provide one; values are normalized via
  `_normalize_language` in `services/crawler.py` (drops `multi`/unknown, maps `zh-cn`→`zh`).

**Changing engines/prompts/chunking** happens in the `lncrawl-translator` package (sibling
repo), not here — bump the dependency version in `pyproject.toml` to pick up a release.
