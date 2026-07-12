---
name: add-job-type
description: Add or modify a background job type in lncrawl — JobType enum, JobService factory, handler class, registry, notifications. Use when creating a new job kind, changing a handler, or debugging job scheduling/cancellation.
---

# Adding a job type

Job execution: `JobScheduler` (services/scheduler/service.py) spawns daemon worker threads —
N general runners (count from `ctx.config.crawler.runner_concurrency`), one dedicated
**artifact-only** worker, one `Scrubber` loop, and one stale-job reset loop. `JobRunner`
(runner.py) claims jobs; handlers in `scheduler/handlers/` execute them.

## The recipe, end to end

1. **Enum** — add a member to `JobType(IntEnum)` in `lncrawl/enums.py` (values are grouped by
   domain; pick a free integer near its siblings). Enums re-export automatically via
   `dao/__init__.py`.
2. **Postgres enum-sync migration** — required because enum columns are stored **by name**
   and are native `ENUM` types on Postgres (SQLite stores VARCHAR, no DDL needed). Model it
   on an existing `sync_*` migration in `migrations/versions/`: raw `op.execute` DDL guarded
   by `op.get_context().dialect.name == 'postgresql'`, no-op otherwise. Alembic autogenerate
   will NOT produce this.
3. **JobService factory** — add a `def my_job(self, user, ..., *, parent_id=None,
   depends_on=None, **data) -> Job` method in `services/jobs/service.py` that funnels into
   `self._create(...)`. `_create` applies tier limits (`ctx.tier.max_active_jobs`), sets
   `priority=ctx.tier.job_priority(user)`, resolves `domain`, and rolls `total` up the
   ancestor chain. If the job hits one source domain and must respect the
   one-running-job-per-domain rule, add its type to `_DOMAIN_JOB_TYPES` and make sure the
   job data lets `_resolve_domain` work (`domain`/`url`/`novel_id`/`chapter_id`).
4. **Handler** — create `services/scheduler/handlers/my_job.py`:
   - `BaseHandler` for a leaf job; `BatchHandler` when the job spawns child jobs.
   - Implement `can_activate(job)` (match on `job.type`) and `run()`.
   - Register it in `_HANDLER_REGISTRY` in `handlers/__init__.py` — **before**
     `FallbackHandler`, which must stay last (it fails any unmatched job).
5. **`job_title`** — add a branch in `Job.job_title` (`dao/job.py`) so the UI/logs render a
   label.
6. **API endpoint** (usually) — a `POST /api/job/create/<hyphenated-kind>` route in
   `server/api/jobs.py` with `Security(ensure_user)` and a Pydantic body model from
   `server/models/`, calling the JobService factory.

## Handler contract (`handlers/_base.py`)

- Constructor gets `(job, signal)`; `process()` wraps `run()` with logging and terminal-state
  handling: `AbortedException` → silent stop, `HandlerException` → failure with its message,
  any other exception → generic failure.
- Helpers `_set_running()`, `_increment()`, `_set_success()`, `_set_failure()`,
  `_set_extra(**values)` commit their own DB session **and call
  `ctx.job_notifier.notify(...)`** — email notifications come for free; don't call the
  notifier manually.
- Idiom inside `run()`: `if not self.job.is_running: self._set_running()`, and poll
  `if self.signal.is_set(): raise AbortedException()` between units of work — cancellation is
  **cooperative**; nothing kills the thread.
- **`BatchHandler.run()` is re-entered repeatedly** until all children are done (its
  `process()` marks success only when every child `is_done`). `run()` must be idempotent —
  guard against re-creating children (see the `added_*` bookkeeping in existing batch
  handlers like `chapter_batch.py`).

## Scheduling model (what to know when debugging)

- Find-and-claim happens in `JobRunner._claim_next()` under a module-level `EventLock`; the
  actual `run_job()` executes outside the lock. Fairness: skips users and domains that
  already have a running claim, then falls back without fairness if nothing matched.
- `_pending` selects PENDING (or just-started RUNNING with no progress) jobs whose
  `depends_on` is done, ordered by priority then age. The artifact worker sees only
  `JobType.ARTIFACT`; general runners see everything else.
- Cancel = set the claim's `Event` (in-memory) + mark the job and its descendants CANCELED in
  DB (`ctx.jobs.cancel`). `reset_stale` re-signals claims older than the configured max age.
- Progress (`done/failed/total`) rolls up ancestor chains via recursive CTEs
  (`services/jobs/utils.py`); a parent auto-completes when `done == total`.
- The `Scrubber` deletes old jobs/tokens/users/activities on its own loop — check it before
  assuming rows persist forever.

## New email notification (only for a new email *type*)

Subclass `MailNotification` (`services/notifications/_base.py`), add a `NotificationItem`
enum member, and register the class in the `NOTIFICATIONS` dict in
`services/notifications/__init__.py`. Delivery is deduped via `job.extra["email_sent"]` and
sent on a background `TaskManager`.
