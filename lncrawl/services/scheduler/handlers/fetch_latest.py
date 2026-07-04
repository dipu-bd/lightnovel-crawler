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
                depends_on=added_types[JobType.NOVEL],
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
