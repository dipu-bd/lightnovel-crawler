from abc import ABC, abstractmethod
from functools import cached_property
from threading import Event
from typing import Any, Callable, List, Optional

from scraper import failure_kind

from ....context import ctx
from ....core.diagnosis import describe, diagnosis_extra
from ....dao import Job, JobStatus
from ....exceptions import AbortedException, ScraperErrorGroup
from ....utils.error_tools import full_traceback, unexpected_message
from ....utils.time_utils import current_timestamp


# ------------------------------------------------------------------ #
#                           Request Handler                          #
# ------------------------------------------------------------------ #
class HandlerException(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class BaseHandler(ABC):
    def __init__(
        self,
        job: Job,
        signal: Optional[Event] = None,
    ) -> None:
        self.job = job
        self.signal = signal or Event()

    @staticmethod
    @abstractmethod
    def can_activate(job: Job) -> bool:
        raise NotImplementedError()

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError()

    def process(self) -> bool:
        self._log_entry()
        return self._guarded(self._set_success)

    # ------------------------------------------------------------------ #
    #                               Helpers                              #
    # ------------------------------------------------------------------ #

    @cached_property
    def user(self):
        return ctx.users.get(self.job.user_id)

    def _log_entry(self):
        message = f"[cyan]{self.job.status.name}[/cyan] [b]{self.job.id}[/b] | {self.job.job_title}"
        if not self.job.parent_job_id:
            ctx.logger.info(message)
        else:
            ctx.logger.debug(message)

    def _set_extra(self, **values: Any) -> None:
        ctx.jobs.update_extra(self.job, values)

    def _set_running(self) -> None:
        with ctx.db.session() as sess:
            now = current_timestamp()
            ctx.jobs._update(
                sess,
                self.job.id,
                started_at=now,
                status=JobStatus.RUNNING,
            )
            sess.commit()
            self.job.started_at = now
            self.job.status = JobStatus.RUNNING

        ctx.job_notifier.notify(self.user, self.job)

    def _increment(self) -> bool:
        with ctx.db.session() as sess:
            ctx.jobs._increment_up(sess, self.job.id)
            sess.commit()
            self.job = sess.get_one(Job, self.job.id)

        ctx.job_notifier.notify(self.user, self.job)
        return True

    def _set_success(self) -> bool:
        with ctx.db.session() as sess:
            ctx.jobs._success(sess, self.job.id)
            sess.commit()
            self.job = sess.get_one(Job, self.job.id)

        ctx.job_notifier.notify(self.user, self.job)
        return True

    def _set_failure(
        self,
        error: str = "",
        err_source: Optional[Exception] = None,
        **extra: Any,
    ) -> bool:
        if err_source is not None:
            extra["traceback"] = full_traceback(err_source)

        with ctx.db.session() as sess:
            ctx.jobs._fail(sess, self.job.id, error.strip(), extra)
            sess.commit()
            self.job = sess.get_one(Job, self.job.id)

        ctx.job_notifier.notify(self.user, self.job)
        return False

    def _guarded(self, on_success: Callable[[], bool]) -> bool:
        try:
            self.run()
            return on_success()
        except AbortedException:
            return False  # ignore error
        except HandlerException as e:
            return self._set_failure(e.message, e)
        except ScraperErrorGroup as e:
            return self._set_diagnosed(e)
        except Exception as e:
            action = self.job.type.name.lower().replace("_", " ")
            return self._set_failure(unexpected_message(e, action), e)

    def _set_diagnosed(self, error: Exception) -> bool:
        """Fail the job with what the retrieval concluded, not with a stack.

        Every member of the group is the site's answer being unusable rather than our
        code breaking, so what the reader needs is the conclusion rather than the frames
        that reached it. The stack is still kept, in `extra` like every other failure —
        it is only the message it is no longer part of.
        """
        reason = failure_kind(error)
        ctx.logger.warn(
            f"[yellow]{reason}[/yellow] [b]{self.job.id}[/b] | {self.job.job_title}",
            exc_info=ctx.logger.is_debug,
        )
        if self.job.domain:
            ctx.health.record(self.job.domain, reason, str(error))
        return self._set_failure(
            describe(error),
            error,
            **diagnosis_extra(error),
        )


# ------------------------------------------------------------------ #
#                           Batch Requests                           #
# ------------------------------------------------------------------ #
class BatchHandler(BaseHandler):
    def __init__(
        self,
        job: Job,
        signal: Optional[Event] = None,
    ) -> None:
        self.children: List[Job] = []
        super().__init__(job, signal)

    def process(self) -> bool:
        self._log_entry()

        if self.job.is_running:
            self.children = ctx.jobs.get_children(self.job.id)
            for job in self.children:
                if not job.is_done:
                    break
            else:
                return self._set_success()

        return self._guarded(self._increment)


# ------------------------------------------------------------------ #
#                               Fallback                             #
# ------------------------------------------------------------------ #
class FallbackHandler(BaseHandler):
    @staticmethod
    def can_activate(job) -> bool:
        return True

    def run(self) -> None:
        raise HandlerException(f"Job type is not supported: {self.job.type!r}")
