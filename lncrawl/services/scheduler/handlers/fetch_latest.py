from ....context import ctx
from ....enums import JobType, OutputFormat
from ._base import AbortedException, BatchHandler, HandlerException


class FetchLatestHandler(BatchHandler):
    @staticmethod
    def can_activate(job) -> bool:
        return job.type == JobType.FETCH_LATEST

    def run(self) -> None:
        novel_id = self.job.extra.get("novel_id")
        novel_title = self.job.extra.get("novel_title")
        if not novel_id:
            raise HandlerException("No novel id")

        added_types = {}
        if self.job.is_running:
            added_types = {job.type: job.id for job in self.children}
        else:
            self._set_running()

        # Step 1: Refresh metadata to pick up any new chapters
        if JobType.NOVEL not in added_types:
            novel = ctx.novels.get(novel_id)
            if ctx.scraper.unchanged(novel.url, self.signal):
                # Reading the table of contents is the expensive half of this job — a
                # paginated one costs a request per page before a single chapter can be
                # skipped — and a 304 says those bytes have not moved, so there is
                # nothing new to list. The missing-chapter pass below still runs:
                # chapters absent from an earlier failure are not new chapters, and
                # skipping the whole job would strand them until the site next changed.
                ctx.logger.debug(f"Contents unchanged, not re-reading: {novel.url}")
            else:
                job = ctx.jobs.fetch_novel(
                    user=self.user,
                    url=novel.url,
                    novel_id=novel_id,
                    novel_title=novel.title,
                    parent_id=self.job.id,
                )
                added_types[job.type] = job.id

        if self.signal.is_set():
            raise AbortedException()

        # Step 2: Queue missing chapters
        if JobType.FETCH_MISSING not in added_types:
            job = ctx.jobs.fetch_missing_chapters(
                self.user,
                novel_id=novel_id,
                novel_title=novel_title,
                parent_id=self.job.id,
                depends_on=added_types.get(JobType.NOVEL),
            )
            added_types[job.type] = job.id

        if self.signal.is_set():
            raise AbortedException()

        # Step 3: Make epub artifact once chapters finish
        if JobType.ARTIFACT not in added_types:
            ctx.jobs.make_artifact(
                self.user,
                novel_id=novel_id,
                format=OutputFormat.epub,
                novel_title=novel_title,
                parent_id=self.job.id,
                depends_on=added_types[JobType.FETCH_MISSING],
            )
