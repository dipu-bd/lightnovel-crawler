import logging
from threading import Event
from typing import Dict

from ...context import ctx
from ...utils.event_lock import EventLock
from .handlers import run_job

logger = logging.getLogger(__name__)

_lock = EventLock()
_queue: Dict[str, Event] = {}
_users: Dict[str, str] = {}
_domains: Dict[str, str] = {}


class JobRunner:
    @staticmethod
    def run(signal: Event, artifact: bool):
        with _lock.using(signal):
            # users currently active by a running job (one job per user)
            active_users = set(_users.values())
            # domains currently being crawled by a running job (one job per domain)
            active_domains = set(_domains.values())
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
            _queue[job.id] = job_signal
            _users[job.id] = job.user_id
            if job.domain:
                _domains[job.id] = job.domain

        # process the current job
        try:
            run_job(job, job_signal)
        finally:
            # release from queue
            with _lock:
                if job.id in _queue:
                    _queue.pop(job.id).set()
                    _users.pop(job.id, None)
                    _domains.pop(job.id, None)

    @staticmethod
    def cancel(job_id: str, cancel_children: bool = True):
        # release from queue and set the signal
        with _lock:
            if job_id in _queue:
                _queue.pop(job_id).set()
                _users.pop(job_id, None)
                _domains.pop(job_id, None)

        # recursively cancel all children as well
        if cancel_children:
            for job_id in ctx.jobs.get_children_ids(job_id):
                JobRunner.cancel(job_id)

    @staticmethod
    def cancel_all():
        # release everything from the queue and set all signals
        with _lock:
            for signal in _queue.values():
                signal.set()
            _queue.clear()
            _users.clear()
            _domains.clear()
