from dataclasses import dataclass
import logging
from threading import Event
from typing import Dict, Optional, Tuple

from ...context import ctx
from ...dao import Job
from ...utils.event_lock import EventLock
from ...utils.time_utils import current_timestamp
from .handlers import run_job

logger = logging.getLogger(__name__)


@dataclass
class _Claim:
    signal: Event
    user_id: str
    domain: Optional[str]
    started_at: int


_lock = EventLock()
_queue: Dict[str, _Claim] = {}


def _release(job_id: str) -> None:
    """Release a claimed job from the queue. Caller must hold _lock."""
    claim = _queue.pop(job_id, None)
    if claim:
        claim.signal.set()


class JobRunner:
    @staticmethod
    def run(signal: Event, artifact: bool):
        while not signal.is_set():
            claimed = JobRunner._claim_next(signal, artifact)
            if not claimed:
                return  # no pending job

            job, job_signal = claimed
            try:
                run_job(job, job_signal)
            except Exception:
                # handlers normally mark their own failures; this is a safety
                # net for errors escaping run_job
                logger.error(f"Unhandled error running job {job.id}", exc_info=True)
                JobRunner._fail_safe(job.id)
            finally:
                # release from queue
                with _lock:
                    _release(job.id)

            # take a rest before continuing
            signal.wait(ctx.config.crawler.runner_cooldown)

    @staticmethod
    def _claim_next(signal: Event, artifact: bool) -> Optional[Tuple[Job, Event]]:
        with _lock.using(signal):
            while not signal.is_set():
                saturated_domains = JobRunner._saturated_domains()
                active_users = {c.user_id for c in _queue.values()}
                # get next pending job for a user that doesn't have any running job
                job = ctx.jobs._pending(
                    artifact,
                    skip_job_ids=_queue.keys(),
                    skip_user_ids=active_users,
                    skip_domains=saturated_domains,
                )
                # if no job for unique users, get pending job for active users.
                # The domain cap stays hard at the source's derived concurrency:
                # one more same-domain job would only block on that source's
                # shared request limiter, wasting a worker.
                if not job:
                    job = ctx.jobs._pending(
                        artifact,
                        skip_job_ids=_queue.keys(),
                        skip_domains=saturated_domains,
                    )
                if not job:
                    return None  # no pending job

                # if it is an internal job, cancel it if it is part of a finished job
                if job.parent_job_id and ctx.jobs.cancel_if_dangling(job):
                    logger.debug(f"Dangling job [b]{job.id}[/b] | {job.job_title}")
                    signal.wait(ctx.config.crawler.runner_cooldown)  # take a rest
                    continue  # dangling job is cancelled; try the next one

                # add the job to queue
                job_signal = Event()
                _queue[job.id] = _Claim(job_signal, job.user_id, job.domain, current_timestamp())
                return job, job_signal
        return None

    @staticmethod
    def _saturated_domains() -> set:
        """Domains that already run as many jobs as their source allows
        concurrent requests. Caller must hold _lock."""
        counts: Dict[str, int] = {}
        for claim in _queue.values():
            if claim.domain:
                counts[claim.domain] = counts.get(claim.domain, 0) + 1
        saturated = set()
        for domain, count in counts.items():
            try:
                limit = ctx.sources.get_crawler(domain).max_concurrency()
            except Exception:
                limit = 1
            if count >= max(1, limit):
                saturated.add(domain)
        return saturated

    @staticmethod
    def _fail_safe(job_id: str) -> None:
        """Best-effort mark a job failed when run_job raised unexpectedly."""
        try:
            with ctx.db.session() as sess:
                ctx.jobs._fail(sess, job_id, "Unexpected runner error")
                sess.commit()
        except Exception:
            logger.error(f"Failed to mark job {job_id} as failed", exc_info=True)

    @staticmethod
    def cancel(job_id: str, cancel_children: bool = True):
        # release from queue and set the signal
        with _lock:
            _release(job_id)

        # recursively cancel all children as well
        if cancel_children:
            for child_id in ctx.jobs.get_children_ids(job_id):
                JobRunner.cancel(child_id)

    @staticmethod
    def cancel_all():
        # release everything from the queue and set all signals
        with _lock:
            for claim in _queue.values():
                claim.signal.set()
            _queue.clear()

    @staticmethod
    def reset_stale(max_age: int) -> None:
        """Cancel only jobs whose claim has been held longer than max_age seconds.

        Recovers genuinely stuck jobs without aborting healthy in-flight ones.
        """
        cutoff = current_timestamp() - max_age * 1000
        with _lock:
            stale = [job_id for job_id, c in _queue.items() if c.started_at < cutoff]
        for job_id in stale:
            logger.warning(f"Resetting stale job [b]{job_id}[/b]")
            JobRunner.cancel(job_id)
