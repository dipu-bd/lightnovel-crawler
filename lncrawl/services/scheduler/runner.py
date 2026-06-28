from dataclasses import dataclass
import logging
from threading import Event
from typing import Dict, Optional

from ...context import ctx
from ...utils.event_lock import EventLock
from .handlers import run_job

logger = logging.getLogger(__name__)


@dataclass
class _Claim:
    signal: Event
    user_id: str
    domain: Optional[str]


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
        with _lock.using(signal):
            # users currently active by a running job (one job per user)
            active_users = {c.user_id for c in _queue.values()}
            # domains currently being crawled by a running job (one job per domain)
            active_domains = {c.domain for c in _queue.values() if c.domain}
            # get next pending job for a user that doesn't have any running job
            job = ctx.jobs._pending(
                artifact,
                skip_job_ids=_queue.keys(),
                skip_user_ids=active_users,
                skip_domains=active_domains,
            )
            # if no job for unique users, get pending job for active users
            if not job:
                job = ctx.jobs._pending(
                    artifact,
                    skip_job_ids=_queue.keys(),
                    skip_domains=active_domains,
                )
            if not job:
                return  # no pending job

            # if it is an internal job, cancel it if it is part of a finished job
            if job.parent_job_id:
                if ctx.jobs.cancel_if_dangling(job):
                    logger.debug(f"Dangling job [b]{job.id}[/b] | {job.job_title}")
                    return

            # add the job to queue
            job_signal = Event()
            _queue[job.id] = _Claim(job_signal, job.user_id, job.domain)

        # process the current job
        try:
            run_job(job, job_signal)
        finally:
            # release from queue
            with _lock:
                _release(job.id)

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
