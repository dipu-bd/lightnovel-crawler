---
name: output-and-translation
description: Binder (e-book output formats) and Translator services — architecture and recipes for adding an output format or a translation backend. Use when working in services/binder/ or services/translators/.
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

# Translator (`lncrawl/services/translators/`)

`TranslationService` holds an **ordered** backend list — the order is the failover priority.
`translate_*` methods try each available backend and return the first success; a backend that
rate-limits (429) is temporarily benched. Chapter translation dedupes via a content hash and
stores results through `ctx.files.save_text`.

**Base classes** (`_base.py`): `BackendBase` (abstract `is_enabled(language)` +
`translate_batch`; provides `translate_html` which splits body-level nodes) and
`ChunkedBackendBase` (packs texts into chunks with a separator, fans out through a
`TaskManager`; subclasses implement single-`translate`). Most real backends extend the
chunked base.

**Recipe — new backend**:
1. Create `backend_<name>.py` subclassing `ChunkedBackendBase`.
2. Implement `is_enabled(language)` (usually a language-map membership test) and
   `translate(text, target, signal=None)` doing HTTP via `with ctx.http.session(signal) as
   sess:` — all backends share the single `FetchService` scraper behind its `EventLock`, and
   the signal participates in cancellation.
3. Insert it into the `_backends` list in `service.py` at the desired failover position.
   Chunking, task management, failover, and `close()` come free.
