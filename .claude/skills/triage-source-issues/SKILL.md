---
name: triage-source-issues
description: Work the GitHub tracker's source backlog — classify requests against the corpus, find duplicates, probe hosts in bulk safely, and close in one pass. Use when asked to reduce open source issues, add requested sources at scale, or survey whether a batch of hosts is still alive.
---

# Triaging the source backlog

Two labels on [the tracker](https://github.com/lncrawl/lightnovel-crawler/issues): **`source`**
asks for a new site, **`source-issue`** reports a broken one. Both accumulate for years, so a
large fraction of any open backlog is already answerable from the repo without touching the
network — and that fraction is where the throughput is.

## Classify before probing

Every issue lands in one of these, and only the last needs a source written:

| bucket | evidence | action |
| --- | --- | --- |
| already supported | host is in the corpus | close, naming the source file |
| duplicate | another open issue names the same host | close against the oldest |
| dead host | probe says parked / DNS gone / refuses | add to `sources/_rejected.json`, close |
| out of scope | not a novel site, or has no chapter list to read | close with the reason |
| real work | host answers and is not supported | write the source |

**Match against the corpus by parsing `base_url` out of every source file, not by grepping for
URLs.** Grep over-counts badly — a URL in a comment, a docstring or a `search` path reads as
support. Walk `sources/` with `ast` and collect the `base_url` assignment from each class.

Two traps in the host-normalising code itself, both of which produced wrong answers here:

- `"www.example.com".lstrip("www.")` strips a *character set*, not a prefix — it also eats the
  leading letters of hosts like `wuxiaworld.ru`. Slice the prefix explicitly.
- A relative `Path("sources")` resolves against the subprocess's cwd, silently yielding an
  empty corpus and classifying everything as unsupported. Use an absolute path and **raise if
  the corpus comes back empty** rather than reporting zeroes.

## Duplicates

**Match on every host a body mentions, not just the first.** A report often names three
mirrors, and the overlap that makes two issues duplicates is frequently on the second or third.
Matching primary-host-to-primary-host finds a small fraction of what is actually there.

Cluster with union-find over "shares at least one host", then close the newer members against
the oldest. Expect clusters, not pairs.

## Judgement calls that should not be automated

Close a request as out of scope only when there is nothing to read. Things that look
out of scope and are not: a site whose requester supplies a URL that *does* carry a chapter
list, and forum-hosted serial fiction where threadmarks are the chapter list. A fanfiction
archive nobody would call a light novel is still scrapable, and "not a light novel" is a
weaker reason to close than "there is no table of contents here".

## Probing hosts in bulk

**Probe through the tor-pool exit, never direct.** A consumer ISP may rewrite blocked domains
to its own page, which answers `200` — so a direct survey both fakes *alive* for a rewritten
host and fakes *dead* for a live one. Every negative result from a direct sweep is worthless.

**Build one `ScraperService` for the whole sweep.** Not one per host, and not one per worker.
Per-origin state is shared deliberately (see the class docstring): separate states do not look
like one visitor going faster, they look like several who contradict each other, and each
flush of a second memory over the same file erases what the first learned.

**Python threads cannot be interrupted.** A worker parked inside a browser solve never returns,
and a thread pool that waits on it loses the entire batch's results — not just that host's.
Run batches as subprocesses under a hard `subprocess.run(timeout=)`, and **write each result
the moment it completes** (JSONL, `as_completed`) so a killed batch still yields everything
that finished.

Two smaller ones worth not rediscovering:

- Do not pipe a long run through `tail` — it buffers, defeating `flush=True`, and a healthy
  run looks stalled at zero bytes for as long as it takes.
- Do not wrap probe internals in `except Exception: pass`. An API used wrongly then reads as
  "the site did not answer", and a whole column comes back empty across an entire sweep with
  nothing indicating why. Check a signature before trusting it — some diagnostics return prose
  for a human, not a dict to index.

## Working a large batch

Three phases, and the value is that phase 2 cannot stall:

1. **Fetch once, in bulk**, and save the HTML to disk per host — listing, novel, chapter.
2. **Write the sources offline**, with no network at all, reading the saved pages. Never
   re-fetch a page that is already saved.
3. **Validate in one pass** at the end, live.

Write a further diagnostic script only when a phase-3 failure cannot be explained from the
saved HTML. The unit of progress is a source file on disk, not a measurement.

Keep durable per-host state in a queue file outside the repo — what was probed, what it
answered, which questions are closed, and why a host is blocked. Read it before probing and
**never re-probe a host that already has a fresh row**. Batch by template rather than by host:
once one WordPress-category site is understood, the rest are minutes each.

**Touch the tracker once, at the very end.** Closing issues as you go interleaves slow network
work with irreversible public writes, and a batch that gets interrupted halfway has then done
the irreversible half.
